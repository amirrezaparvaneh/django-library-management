from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import BookForm, CategoryForm, SignUpForm
from .models import Book, Category, Favorite


def filtered_books(request, params=None):
    params = params or request.GET
    query = params.get("q", "").strip()
    availability = params.get("availability", "all")
    category_id = params.get("category", "").strip()
    min_price_raw, max_price_raw = params.get("min_price", "").strip(), params.get("max_price", "").strip()
    date_from_raw, date_to_raw = params.get("date_from", "").strip(), params.get("date_to", "").strip()
    errors = []
    books = Book.objects.prefetch_related("categories").all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if availability == "available":
        books = books.filter(is_available=True)
    elif availability == "unavailable":
        books = books.filter(is_available=False)
    elif availability != "all":
        errors.append("The selected availability status is invalid.")
    if category_id:
        if category_id.isdigit() and Category.objects.filter(pk=category_id).exists():
            books = books.filter(categories__id=int(category_id))
        else:
            errors.append("The selected category is invalid.")
    try:
        if min_price_raw:
            books = books.filter(price__gte=Decimal(min_price_raw))
        if max_price_raw:
            books = books.filter(price__lte=Decimal(max_price_raw))
    except InvalidOperation:
        errors.append("Price must be a valid number.")
    if date_from_raw:
        try:
            books = books.filter(publication_date__gte=date.fromisoformat(date_from_raw))
        except ValueError:
            errors.append("The start date is invalid.")
    if date_to_raw:
        try:
            books = books.filter(publication_date__lte=date.fromisoformat(date_to_raw))
        except ValueError:
            errors.append("The end date is invalid.")
    return books.distinct().order_by("-created_at"), {
        "query": query, "availability": availability, "category_id": category_id,
        "min_price": min_price_raw, "max_price": max_price_raw,
        "date_from": date_from_raw, "date_to": date_to_raw, "filter_errors": errors,
    }


def book_list(request):
    books, filters = filtered_books(request)
    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(Favorite.objects.filter(user=request.user, book__in=page_obj.object_list).values_list("book_id", flat=True))
    return render(request, "books/book_list.html", {
        "books": page_obj, "page_obj": page_obj, "categories": Category.objects.order_by("name"),
        "favorite_ids": favorite_ids, **filters,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.prefetch_related("categories"), pk=pk)
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, book=book).exists()
    return render(request, "books/book_detail.html", {"book": book, "is_favorite": is_favorite})


def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect("book_list")
    return render(request, "books/book_form.html", {"form": form, "title": "Add Book"})


def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book updated successfully.")
        return redirect("book_list")
    return render(request, "books/book_form.html", {"form": form, "title": "Edit Book", "book": book})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted.")
    return redirect("book_list")


def bulk_delete(request):
    if request.method == "POST":
        books, filters = filtered_books(request, request.POST)
        if filters["filter_errors"]:
            messages.error(request, "No books were deleted because the filters are invalid.")
            return redirect("book_list")
        count = books.count()
        if count:
            books.delete()
            messages.success(request, f"{count} book(s) deleted.")
        else:
            messages.warning(request, "There are no results to delete.")
    return redirect("book_list")


@login_required
def toggle_favorite(request, pk):
    if request.method == "POST":
        book = get_object_or_404(Book, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
        if not created:
            favorite.delete()
        messages.success(request, "Favorite status updated.")
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "book_list"
    return redirect(next_url)


@login_required
def favorites(request):
    books = Book.objects.filter(favorited_by__user=request.user).prefetch_related("categories")
    return render(request, "books/favorites.html", {"books": books})


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Registration successful.")
        return redirect("book_list")
    return render(request, "books/auth_form.html", {"form": form, "title": "Sign Up"})


def signin(request):
    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-control"
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("book_list")
    return render(request, "books/auth_form.html", {"form": form, "title": "Log In"})


@login_required
def signout(request):
    if request.method == "POST":
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect("book_list")


def category_list(request):
    categories = Category.objects.order_by("name")
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category added successfully.")
        return redirect("category_list")
    return render(request, "books/category_list.html", {"categories": categories, "form": form})

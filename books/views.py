from django.db.models import Q
from django.shortcuts import render

from .models import Book


def book_list(request):
    query = request.GET.get("q", "").strip()
    availability = request.GET.get("availability", "all")

    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(isbn=query)
            | Q(isbn__icontains=query)
        )

    if availability == "available":
        books = books.filter(is_available=True)
    elif availability == "unavailable":
        books = books.filter(is_available=False)

    return render(
        request,
        "books/book_list.html",
        {
            "books": books,
            "query": query,
            "availability": availability,
        },
    )

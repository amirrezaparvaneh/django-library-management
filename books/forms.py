from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book, Category


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "isbn", "publication_date", "publication_year", "price", "categories", "description", "is_available")
        widgets = {
            "publication_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "title": "Title", "author": "Author", "isbn": "ISBN",
            "publication_date": "Publication date", "publication_year": "Publication year",
            "price": "Price", "categories": "Categories",
            "description": "Description", "is_available": "Available",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-select" if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else "form-control"
            field.widget.attrs["class"] = css_class

    def clean_title(self):
        value = self.cleaned_data["title"].strip()
        if not value:
            raise forms.ValidationError("Title is required.")
        return value

    def clean_author(self):
        value = self.cleaned_data["author"].strip()
        if not value:
            raise forms.ValidationError("Author is required.")
        return value

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_isbn(self):
        isbn = (self.cleaned_data.get("isbn") or "").replace("-", "").replace(" ", "")
        if isbn and (not isbn.isdigit() or len(isbn) not in (10, 13)):
            raise forms.ValidationError("ISBN must contain 10 or 13 digits.")
        return isbn or None


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
        labels = {"name": "Category name"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["class"] = "form-control"


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "Username", "email": "Email"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

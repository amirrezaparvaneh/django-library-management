from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "isbn",
        "publication_year",
        "is_available",
    )
    list_filter = ("is_available", "publication_year")
    search_fields = ("title", "author", "isbn")

    list_editable = ("is_available",)
    ordering = ("title",)
    list_per_page = 20


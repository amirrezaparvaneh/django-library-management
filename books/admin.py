from django.contrib import admin

from .models import Book, Category, Favorite

admin.site.register(Category)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "created_at")


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

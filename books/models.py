from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        blank=True,
    )
    publication_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    description = models.TextField(
        blank=True,
    )
    is_available = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return self.title
from django.test import TestCase
from django.urls import reverse

from .models import Book


class BookListFilterTest(TestCase):
    def setUp(self):
        Book.objects.create(
            title="Available Book",
            author="Author One",
            isbn="1111111",
            publication_year=2020,
            is_available=True,
        )

        Book.objects.create(
            title="Unavailable Book",
            author="Author Two",
            isbn="2222222222",
            publication_year=2021,
            is_available=False,
        )

    def test_book_list_shows_all_books(self):
        response = self.client.get(
            reverse("book_list"),
            {"availability": "all"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 2)

    def test_book_list_shows_available_books(self):
        response = self.client.get(
            reverse("book_list"),
            {"availability": "available"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 1)
        self.assertContains(response, "Available Book")
        self.assertNotContains(response, "Unavailable Book")

    def test_book_list_shows_unavailable_books(self):
        response = self.client.get(
            reverse("book_list"),
            {"availability": "unavailable"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 1)
        self.assertContains(response, "Unavailable Book")
        self.assertNotContains(response, "Available Book")

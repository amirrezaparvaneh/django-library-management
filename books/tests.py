from datetime import date

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from .models import Book, Category, Favorite


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


class LibraryCrudAndAuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("reader", password="Strong-pass-123")
        self.category = Category.objects.create(name="Programming")
        self.book = Book.objects.create(
            title="Django By Example", author="Antonio", price="25.50",
            publication_year=2024, publication_date=date(2024, 4, 10),
        )
        self.book.categories.add(self.category)

    def test_create_edit_delete_book(self):
        response = self.client.post(reverse("book_create"), {
            "title": "New Book", "author": "Writer", "price": "10",
            "categories": [self.category.pk], "is_available": "on",
        })
        self.assertRedirects(response, reverse("book_list"))
        created = Book.objects.get(title="New Book")
        self.client.post(reverse("book_edit", args=[created.pk]), {
            "title": "Edited", "author": "Writer", "price": "11", "is_available": "on",
        })
        self.assertTrue(Book.objects.filter(title="Edited").exists())
        self.client.post(reverse("book_delete", args=[created.pk]))
        self.assertFalse(Book.objects.filter(pk=created.pk).exists())

    def test_invalid_book_is_not_created(self):
        response = self.client.post(reverse("book_create"), {"title": " ", "author": "", "price": "-1"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.filter(title=" ").exists())
        self.assertContains(response, "This field is required.")

    def test_search_by_title_and_author_is_partial_and_case_insensitive(self):
        self.assertEqual(self.client.get(reverse("book_list"), {"q": "DJANGO"}).context["page_obj"].paginator.count, 1)
        self.assertEqual(self.client.get(reverse("book_list"), {"q": "tonio"}).context["page_obj"].paginator.count, 1)

    def test_search_price_category_and_bulk_delete(self):
        Book.objects.create(title="Outside", author="Other", price="5")
        response = self.client.get(reverse("book_list"), {
            "q": "django", "min_price": "20", "category": self.category.pk,
            "date_from": "2024-01-01", "date_to": "2024-12-31",
        })
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.client.post(reverse("bulk_delete"), {
            "q": "django", "min_price": "20", "category": self.category.pk,
            "date_from": "2024-01-01", "date_to": "2024-12-31",
        })
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
        self.assertTrue(Book.objects.filter(title="Outside").exists())

    def test_invalid_bulk_filter_deletes_nothing(self):
        self.client.post(reverse("bulk_delete"), {"min_price": "not-a-number"})
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_favorites_are_private_and_unique(self):
        self.client.login(username="reader", password="Strong-pass-123")
        self.client.post(reverse("toggle_favorite", args=[self.book.pk]))
        self.client.post(reverse("toggle_favorite", args=[self.book.pk]))
        self.assertFalse(Favorite.objects.filter(user=self.user, book=self.book).exists())
        self.client.post(reverse("toggle_favorite", args=[self.book.pk]))
        response = self.client.get(reverse("favorites"))
        self.assertContains(response, self.book.title)
        other = User.objects.create_user("other", password="Strong-pass-123")
        other_book = Book.objects.create(title="Private Favorite", author="Writer")
        Favorite.objects.create(user=other, book=other_book)
        self.assertNotContains(response, other_book.title)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Favorite.objects.create(user=self.user, book=self.book)

    def test_signup_and_protected_favorites(self):
        self.assertRedirects(self.client.get(reverse("favorites")), "/login/?next=/favorites/")
        response = self.client.post(reverse("signup"), {
            "username": "newreader", "email": "new@example.com",
            "password1": "Another-strong-123", "password2": "Another-strong-123",
        })
        self.assertRedirects(response, reverse("book_list"))

    def test_login_and_post_logout(self):
        response = self.client.post(reverse("login"), {"username": "reader", "password": "Strong-pass-123"})
        self.assertRedirects(response, reverse("book_list"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.get(reverse("logout"))
        self.assertIn("_auth_user_id", self.client.session)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_category_creation_and_book_connection(self):
        self.client.post(reverse("category_list"), {"name": "History"})
        history = Category.objects.get(name="History")
        self.client.post(reverse("book_edit", args=[self.book.pk]), {
            "title": self.book.title, "author": self.book.author,
            "price": self.book.price, "categories": [history.pk], "is_available": "on",
        })
        self.assertEqual(list(self.book.categories.values_list("name", flat=True)), ["History"])

    def test_csrf_protects_mutating_requests(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(reverse("book_delete", args=[self.book.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

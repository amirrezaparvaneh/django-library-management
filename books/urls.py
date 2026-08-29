from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.book_list, name="book_list"),
    path("books/", views.book_list, name="books"),
    path("books/add/", views.book_create, name="book_create"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/edit/", views.book_edit, name="book_edit"),
    path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("books/delete-filtered/", views.bulk_delete, name="bulk_delete"),
    path("books/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("favorites/", views.favorites, name="favorites"),
    path("categories/", views.category_list, name="category_list"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.signin, name="login"),
    path("logout/", views.signout, name="logout"),
]

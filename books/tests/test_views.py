from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from authors.models import Author, BookAuthor
from books.models import Book


User = get_user_model()


class BooksViewsTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            email="adminadmin@admin.com", password="adminpass"
        )
        self.regular_user = User.objects.create_user(
            email="useruser@user.com", password="userpass"
        )

        self.author = Author.objects.create(
            first_name="Author 1", last_name="First Author"
        )
        self.book = Book.objects.create(
            title="Test Book", inventory=5, cover="Soft", daily_fee=2.0
        )
        BookAuthor.objects.create(book=self.book, author=self.author)

        self.list_url = reverse("books:books-list")
        self.detail_url = reverse("books:books-detail", args=[self.book.id])

    def test_list_books_avilable_for_anyone(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], self.book.title)

    def test_retrieve_book_allowed_for_anyone(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], self.book.title)

    def test_create_book_denied_for_anonymous(self):
        data = {
            "title": "New Book",
            "inventory": 3,
            "cover": "Hard",
            "daily_fee": 1.5,
            "authors": [self.author.id],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 401)

    def test_create_book_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "title": "Admin Book",
            "inventory": 7,
            "cover": "Soft",
            "daily_fee": 3.0,
            "authors": [self.author.id],
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book_denied_for_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.detail_url, {"title": "Updated by user"})
        self.assertEqual(response.status_code, 403)

    def test_update_book_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.detail_url, {"title": "Updated by admin"})
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Updated by admin")

    def test_destroy_book_allowed_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())

    def test_destroy_book_denied_for_regular_user(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)

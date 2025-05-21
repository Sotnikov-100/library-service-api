from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from authors.models import Author
from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()


class BorrowingsViewsTest(TestCase):

    def setUp(self: Borrowing) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            email="superuser@library.com",
            password="testpassword"
        )
        self.reader_user = User.objects.create_user(
            email="reader@library.com",
            password="usertestpass"
        )

        self.author = Author.objects.create(
            first_name="Author",
            last_name="First"
        )
        self.book = Book.objects.create(
            title="Test Book",
            inventory=5,
            cover="Soft",
            daily_fee=3.0
        )

        data = {
            "user": self.admin_user,
            "book": self.book,
            "borrow_date": "2025-05-21",
            "expected_return_date": "2025-05-28",
        }
        Borrowing.objects.create(**data)

        self.list_url = reverse("borrowings:borrowings-list")

    def test_list_borrowings_not_available_for_unautthenticated(self: Borrowing) -> None:
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

    def test_create_borrowing_not_allowed_for_reader(self: Borrowing) -> None:
        self.client.force_authenticate(user=self.reader_user)

        data_2 = {
            "user": self.admin_user,
            "book": self.book,
            "borrow_date": "2025-05-11",
            "expected_return_date": "2025-05-18",
        }

        response = self.client.post(self.list_url, data_2)
        self.assertEqual(response.status_code, 400)


class BorrowingCreateViewTest(APITestCase):

    def setUp(self: Borrowing) -> None:
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="testpass123"
        )
        self.author = Author.objects.create(
            first_name="Test",
            last_name="Author"
        )
        self.book = Book.objects.create(
            title="Test Book",
            inventory=5,
            daily_fee=1.5,
            cover="Hard",
        )
        self.book.authors.add(self.author)

        self.url = reverse("borrowings:borrowings-list")

    def test_create_borrowing_authenticated(self: Borrowing) -> None:
        """Test that authenticated user can create borrowing"""
        self.client.force_authenticate(user=self.user)
        data = {
            "book": self.book.id,
            "borrow_date": "2025-05-21",
            "expected_return_date": "2025-05-28",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        borrowing = Borrowing.objects.first()
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)

    def test_create_borrowing_unauthenticated(self: Borrowing) -> None:
        """Test that unauthenticated user cannot create borrowing"""
        data = {
            "book": self.book.id,
            "borrow_date": "2025-05-21",
            "expected_return_date": "2025-05-28",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Borrowing.objects.count(), 0)

    def test_create_borrowing_with_invalid_dates(self: Borrowing) -> None:
        """Test that borrowing is not created if expected_return_date is before borrow_date"""
        self.client.force_authenticate(user=self.user)
        data = {
            "book": self.book.id,
            "borrow_date": "2025-05-28",
            "expected_return_date": "2025-05-21",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expected_return_date", response.data)
        self.assertEqual(Borrowing.objects.count(), 0)

    def test_create_borrowing_with_no_inventory(self) -> None:
        """Test that borrowing cannot be created if book inventory is 0"""
        self.client.force_authenticate(user=self.user)
        self.book.inventory = 0
        self.book.save()

        data = {
            "book": self.book.id,
            "borrow_date": "2025-05-21",
            "expected_return_date": "2025-05-28",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authors.models import Author
from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingCreateSerializer


class BooksSerializersTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="First",
            last_name="Last"
        )
        self.book = Book.objects.create(
            title="test_title",
            inventory=100,
            cover="Hard",
            daily_fee=0.01,
        )
        self.book.authors.add(self.author)
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@library.test", "password",
        )
        self.client.force_authenticate(self.user)

    def test_borrowing_serializer_valid_data_creates_instance(self) -> None:
        data = {
            "book": self.book.id,
            "borrow_date": "2025-05-21",
            "expected_return_date": "2025-05-28",
        }

        class DummyRequest:
            def __init__(self, user):
                self.user = user

        serializer = BorrowingCreateSerializer(
            data=data,
            context={"request": DummyRequest(self.user)}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        borrowing = serializer.save()

        self.assertEqual(Borrowing.objects.count(), 1)
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)

    def test_borrowing_serializer_invalid_dates(self: Borrowing) -> None:
        data = {
            "book": self.book.id,
            "borrow_date": "2025-05-21",
            "expected_return_date": "2025-05-20",
        }

        class DummyRequest:
            def __init__(self, user):
                self.user = user

        serializer = BorrowingCreateSerializer(
            data=data,
            context={"request": DummyRequest(self.user)}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("expected_return_date", serializer.errors)

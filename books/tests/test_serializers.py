from django.test import TestCase
from authors.models import Author, BookAuthor
from books.models import Book
from books.serializers import BookSerializer, BookCreateUpdateSerializer


class BooksSerializersTest(TestCase):

    def setUp(self):
        self.author1 = Author.objects.create(
            first_name="Author 1", last_name="First Author"
        )
        self.author2 = Author.objects.create(
            first_name="Author 2", last_name="Second Author"
        )

    def test_daily_fee_validation_negative(self):
        data = {
            "title": "Test Book",
            "inventory": 5,
            "cover": "Soft",
            "daily_fee": -5.0,
            "authors": [self.author1.id],
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_fee", serializer.errors)

    def test_inventory_validation_negative(self):
        data = {
            "title": "Test Book",
            "inventory": -3,
            "cover": "Hard",
            "daily_fee": 4.0,
            "authors": [self.author1.id],
        }
        serializer = BookCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("inventory", serializer.errors)

    def test_create_book_with_authors(self):
        data = {
            "title": "New Book",
            "inventory": 10,
            "cover": "Soft",
            "daily_fee": 2.5,
            "authors": [self.author1.id, self.author2.id],
        }
        serializer = BookCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        book = serializer.save()

        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(BookAuthor.objects.filter(book=book).count(), 2)

    def test_update_book_with_new_authors(self):
        book = Book.objects.create(
            title="Old Title",
            inventory=5,
            cover="Hard",
            daily_fee=1.5,
        )
        BookAuthor.objects.create(book=book, author=self.author1)

        data = {
            "title": "Updated Title",
            "inventory": 7,
            "cover": "Soft",
            "daily_fee": 3.0,
            "authors": [self.author2.id],
        }

        serializer = BookCreateUpdateSerializer(book, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_book = serializer.save()

        self.assertEqual(updated_book.title, "Updated Title")
        self.assertEqual(updated_book.authors.count(), 1)
        self.assertEqual(updated_book.authors.first(), self.author2)

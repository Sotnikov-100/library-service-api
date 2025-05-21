from django.test import TestCase, RequestFactory
from unittest.mock import patch
from payments.services import create_stripe_session, send_telegram_notification
from payments.models import Payment
from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentServicesTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(email="user@test.com", password="password")
        self.book = Book.objects.create(
            title="Test Book", cover="HARD", inventory=3, daily_fee=2.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2023-01-01",
            expected_return_date="2023-01-08",
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="PAYMENT",
            session_url="https://example.com",
            session_id="sess_123",
            money_to_pay=100,
        )

    @patch("stripe.checkout.Session.create")
    def test_create_stripe_session(self, mock_stripe):
        mock_stripe.return_value = type(
            "obj", (object,), {"url": "https://stripe.com/test", "id": "stripe_test_id"}
        )

        request = self.factory.get("/")
        create_stripe_session(self.payment, request)
        self.payment.refresh_from_db()

        self.assertEqual(self.payment.session_url, "https://stripe.com/test")
        self.assertEqual(self.payment.session_id, "stripe_test_id")

    @patch("requests.post")
    def test_telegram_notification(self, mock_post):
        send_telegram_notification(self.payment)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_telegram_notification_failure(self, mock_post):
        mock_post.side_effect = Exception("API Error")
        with self.assertRaises(Exception):
            send_telegram_notification(self.payment)

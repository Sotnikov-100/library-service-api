from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.utils import timezone
from payments.tasks import check_expired_payments
from payments.models import Payment, PaymentStatus
from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentTasksTests(TestCase):
    def setUp(self):
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

    @patch("payments.tasks.stripe.checkout.Session.retrieve")
    def test_expired_payment_handling(self, mock_stripe):
        mock_session = MagicMock()
        mock_session.status = "expired"
        mock_stripe.return_value = mock_session

        old_payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="expired_123",
            money_to_pay=10.00,
            status=PaymentStatus.PENDING,
        )
        old_payment.created_at = timezone.now() - timedelta(days=2)
        old_payment.save(update_fields=["created_at"])

        check_expired_payments()
        old_payment.refresh_from_db()
        self.assertEqual(old_payment.status, PaymentStatus.EXPIRED)

    @patch("stripe.checkout.Session.retrieve")
    def test_expired_payment_stripe_error(self, mock_stripe):
        mock_stripe.side_effect = Exception("Stripe Error")

        old_payment = Payment.objects.create(
            borrowing=self.borrowing,
            created_at=timezone.now() - timedelta(days=2),
            session_id="expired_123",
            money_to_pay=10.00,
        )

        check_expired_payments()
        old_payment.refresh_from_db()
        self.assertEqual(old_payment.status, PaymentStatus.PENDING)

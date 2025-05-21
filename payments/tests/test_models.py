from django.test import TestCase
from datetime import timedelta
from django.utils import timezone
from payments.models import Payment, PaymentStatus, PaymentType
from borrowings.models import Borrowing
from books.models import Book
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="password")
        self.book = Book.objects.create(
            title="Test Book", cover="HARD", inventory=3, daily_fee=2.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7),
        )

    def test_payment_str_representation(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_url="https://test.com",
            session_id="test123",
            money_to_pay=10.00,
        )
        self.assertEqual(
            str(payment), f"{self.user.email} - {payment.type} - {payment.status}"
        )

    def test_payment_default_status(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_url="https://test.com",
            session_id="test123",
            money_to_pay=10.00,
        )
        self.assertEqual(payment.status, PaymentStatus.PENDING)

    def test_payment_default_type(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_url="https://test.com",
            session_id="test123",
            money_to_pay=10.00,
        )
        self.assertEqual(payment.type, PaymentType.PAYMENT)

    def test_payment_invalid_money_to_pay(self):
        with self.assertRaises(ValidationError):
            payment = Payment(
                borrowing=self.borrowing,
                session_url="https://test.com",
                session_id="test123",
                money_to_pay=-10.00,
            )
            payment.full_clean()

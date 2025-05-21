from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from payments.models import Payment, PaymentStatus
from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="password")
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="password"
        )
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
            status=PaymentStatus.PENDING,
            type="PAYMENT",
            session_url="https://example.com",
            session_id="sess_123",
            money_to_pay=100,
        )

    def test_renew_session_action(self):
        self.client.force_login(self.user)
        self.payment.status = PaymentStatus.EXPIRED
        self.payment.save()

        response = self.client.post(
            reverse("payments:payments-renew-session", args=[self.payment.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("session_url", response.data)

    def test_renew_session_invalid_status(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("payments:payments-renew-session", args=[self.payment.id])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_admin_payment_listing(self):
        self.client.force_login(self.admin)
        response = self.client.get("/admin/payments/payment/")
        self.assertContains(response, str(self.payment.id))

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment, PaymentType, PaymentStatus


User = get_user_model()


class PaymentViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="password")
        self.other_user = User.objects.create_user(email="other@test.com", password="password")
        self.admin = User.objects.create_superuser(email="admin@test.com", password="password")

        self.book = Book.objects.create(
            title="Django for Testers",
            cover="HARD",
            inventory=3,
            daily_fee=2.00
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7)
        )

        self.other_borrowing = Borrowing.objects.create(
            user=self.other_user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7)
        )

        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            type=PaymentType.PAYMENT,
            status=PaymentStatus.PENDING,
            session_url="https://example.com",
            session_id="sess_123",
            money_to_pay=100
        )

        self.other_payment = Payment.objects.create(
            borrowing=self.other_borrowing,
            type=PaymentType.PAYMENT,
            status=PaymentStatus.PENDING,
            session_url="https://example.com",
            session_id="sess_456",
            money_to_pay=50
        )

    def test_user_can_list_their_payments(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("payments:payments-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.payment.id)

    def test_user_can_retrieve_own_payment(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("payments:payments-detail", args=[self.payment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.payment.id)

    def test_user_cannot_retrieve_others_payment(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("payments:payments-detail", args=[self.other_payment.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_list_all_payments(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments:payments-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_cannot_delete_payment(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("payments:payments-detail", args=[self.payment.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        url = reverse("payments:payments-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

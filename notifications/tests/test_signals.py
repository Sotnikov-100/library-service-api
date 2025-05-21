from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch

from django.contrib.auth import get_user_model
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment, PaymentType, PaymentStatus
from tgaccounts.models import TelegramAccount

User = get_user_model()


class TestDataCreationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            cover="HARD",
            inventory=5,
            daily_fee=10.00
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timedelta(days=7)
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            type=PaymentType.PAYMENT,
            status=PaymentStatus.PENDING,
            session_url="https://test.com/session",
            session_id="test_session_123",
            money_to_pay=70.00
        )
        self.telegram_account = TelegramAccount.objects.create(
            user=self.user,
            chat_id="123456789",
            bind_token="test_token_123"
        )

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_user_creation(self, mock_send_task, mock_create_task):
        """Test user creation and attributes"""
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_book_creation(self, mock_send_task, mock_create_task):
        """Test book creation and attributes"""
        book = Book.objects.get(title="Test Book")
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.cover, "HARD")
        self.assertEqual(book.inventory, 5)
        self.assertEqual(book.daily_fee, 10.00)

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_payment_creation(self, mock_send_task, mock_create_task):
        """Test payment creation and relationships"""
        payment = Payment.objects.get(borrowing=self.borrowing)
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.type, PaymentType.PAYMENT)
        self.assertEqual(payment.status, PaymentStatus.PENDING)
        self.assertEqual(payment.session_url, "https://test.com/session")
        self.assertEqual(payment.session_id, "test_session_123")
        self.assertEqual(payment.money_to_pay, 70.00)

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_telegram_account_creation(self, mock_send_task, mock_create_task):
        """Test telegram account creation and relationships"""
        telegram_account = TelegramAccount.objects.get(user=self.user)
        self.assertEqual(telegram_account.user, self.user)
        self.assertEqual(telegram_account.chat_id, "123456789")
        self.assertEqual(telegram_account.bind_token, "test_token_123")

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_borrowing_payment_relationship(self, mock_send_task, mock_create_task):
        """Test relationship between borrowing and payment"""
        self.assertEqual(self.borrowing.payments.count(), 1)
        self.assertEqual(self.borrowing.payments.first(), self.payment)
        self.assertEqual(self.payment.borrowing, self.borrowing)

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_user_telegram_relationship(self, mock_send_task, mock_create_task):
        """Test relationship between user and telegram account"""
        self.assertEqual(self.user.telegram_account, self.telegram_account)
        self.assertEqual(self.telegram_account.user, self.user)

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_book_inventory_update(self, mock_send_task, mock_create_task):
        """Test book inventory update after borrowing"""
        initial_inventory = self.book.inventory
        self.book.inventory -= 1
        self.book.save()
        self.assertEqual(self.book.inventory, initial_inventory - 1)

    @patch('notifications.tasks.create_notification_task.delay')
    @patch('notifications.tasks.send_notification_task.delay')
    def test_payment_status_update(self, mock_send_task, mock_create_task):
        """Test payment status update"""
        self.payment.status = PaymentStatus.PAID
        self.payment.save()
        self.assertEqual(self.payment.status, PaymentStatus.PAID)

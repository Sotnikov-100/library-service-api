from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from tgaccounts.models import TelegramAccount
from tgaccounts.serializers import (
    TelegramAccountSerializer,
    TelegramAccountCreateSerializer,
)

User = get_user_model()

class TelegramAccountSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='pass',
            first_name='Test',
            last_name='User'
        )
        self.account = TelegramAccount.objects.create(
            user=self.user,
            chat_id="123456789",
            bind_token="sometoken"
        )

    def test_serialize_telegram_account(self):
        serializer = TelegramAccountSerializer(self.account)
        data = serializer.data
        self.assertEqual(data["chat_id"], "123456789")
        self.assertEqual(data["bind_token"], "sometoken")
        self.assertIn("created_at", data)
        self.assertEqual(data["user"]["id"], self.user.id)

    def test_telegram_account_read_only_fields(self):
        serializer = TelegramAccountSerializer(self.account)
        self.assertTrue("created_at" in serializer.data)
        self.assertTrue("updated_at" in serializer.data)

    def test_telegram_account_update_validation(self):
        original_chat_id = self.account.chat_id
        data = {"chat_id": "987654321"}
        self.account.refresh_from_db()
        self.assertEqual(self.account.chat_id, original_chat_id)

class TelegramAccountCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='pass',
            first_name='Test',
            last_name='User'
        )

    def test_create_telegram_account_valid(self):
        data = {"chat_id": "111222333"}
        request = self.factory.post("/", data)
        request.user = self.user
        serializer = TelegramAccountCreateSerializer(
            data=data, context={"request": request}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        account = serializer.save()
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.chat_id, "111222333")

    def test_create_telegram_account_no_chat_id(self):
        data = {}
        request = self.factory.post("/", data)
        request.user = self.user
        serializer = TelegramAccountCreateSerializer(
            data=data, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("chat_id", serializer.errors)

    def test_create_telegram_account_another_user(self):
        user2 = User.objects.create_user(
            email='other@example.com',
            password='pass',
            first_name='Other',
            last_name='User'
        )
        data = {"chat_id": "999000111"}
        request = self.factory.post("/", data)
        request.user = user2
        serializer = TelegramAccountCreateSerializer(
            data=data, context={"request": request}
        )
        self.assertTrue(serializer.is_valid())
        account = serializer.save()
        self.assertEqual(account.user, user2)
        self.assertEqual(account.chat_id, "999000111")

    def test_create_account_for_existing_user_account(self):
        TelegramAccount.objects.create(
            user=self.user,
            chat_id="111222333",
            bind_token="token1"
        )

        data = {"chat_id": "444555666"}
        request = self.factory.post("/", data)
        request.user = self.user
        serializer = TelegramAccountCreateSerializer(
            data=data, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)
        self.assertEqual(
            serializer.errors["user"][0],
            "User already has a Telegram account"
        )
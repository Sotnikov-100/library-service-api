from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from config.settings import TELEGRAM_BOT_NAME
from tgaccounts.models import TelegramAccount

User = get_user_model()


class TgBotLinkViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('tgaccounts:get_telegram_link')

    def test_get_bot_link(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['telegram_bot_link'],
            f'https://t.me/{TELEGRAM_BOT_NAME}'
        )


class TelegramAccountViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.telegram_account = TelegramAccount.objects.create(
            user=self.user,
            chat_id='123456789'
        )
        self.url = reverse('tgaccounts:tg-accounts-detail', kwargs={'pk': self.telegram_account.pk})

    def test_retrieve_telegram_account(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['chat_id'], self.telegram_account.chat_id)

    def test_retrieve_telegram_account_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_delete_telegram_account(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TelegramAccount.objects.filter(id=self.telegram_account.id).exists())


class TelegramAccountRegisterViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        self.chat_id = '123456789'
        self.url = reverse('tgaccounts:tg_account_register', kwargs={'chat_id': self.chat_id})

    def test_register_telegram_account(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TelegramAccount.objects.filter(
            user=self.user,
            chat_id=self.chat_id
        ).exists())

    def test_register_telegram_account_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_register_telegram_account_duplicate_chat_id(self):
        # Create existing account with same chat_id
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        TelegramAccount.objects.create(
            user=other_user,
            chat_id=self.chat_id
        )
        data = {
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

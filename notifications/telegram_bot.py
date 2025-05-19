import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

from notifications.models import Notification

load_dotenv()

class TelegramNotification:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_API_TOKEN")
        self.bot = Bot(token=self.token)

    async def send_notification(self, message: str, chat_id: int):
        await self.bot.send_message(chat_id=chat_id, text=message)

class TGNotificationService:
    def __init__(self):
        self.notifier = TelegramNotification()

    def create_notification(self, user, message, chat_id):
        notification = Notification.objects.create(
            user=user,
            message=message,
            chat_id=chat_id,
        )
        asyncio.create_task(self.notifier.send_notification(message, chat_id))
        return notification
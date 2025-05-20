import os
import asyncio
from telegram import Bot

from notifications.models import Notification

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")


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
        )
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self.notifier.send_notification(message, chat_id))
        return notification

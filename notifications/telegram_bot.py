import asyncio
import logging
import os

from telegram import Bot

logger = logging.getLogger(__name__)


class TelegramNotification:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_API_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_API_TOKEN is not set in environment variables")
        self.bot = Bot(token=self.token)

    async def send_notification(self, message: str, chat_id: int):
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False

class TelegramNotificationService:
    """
    Service for sending notifications via Telegram.
    Supports usage in both synchronous and asynchronous code.
    """
    def __init__(self):
        self.notifier = TelegramNotification()

    def send(self, message: str, chat_id: int) -> bool:
        """
        Synchronous method to send a message.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            raise RuntimeError(
                "Cannot call sync send inside a running event loop. Use send_async instead."
            )
        return asyncio.run(self.notifier.send_notification(message=message, chat_id=chat_id))

    async def send_async(self, message: str, chat_id: int) -> bool:
        """
        Asynchronous method to send a message.
        """
        return await self.notifier.send_notification(message=message, chat_id=chat_id)

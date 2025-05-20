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


class TGNotificationService:
    def __init__(self):
        try:
            self.notifier = TelegramNotification()
        except ValueError as e:
            print(f"Telegram notification service initialization failed: {str(e)}")
            self.notifier = None

    def create_notification(self, user, message):
        notification = Notification.objects.create(
            user=user, message=message, is_sent=False
        )

        if not self.notifier:
            return notification

        # Check if user has telegram account
        if not hasattr(user, "telegram_account"):
            return notification

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            success = loop.run_until_complete(
                self.notifier.send_notification(
                    message=message, chat_id=user.telegram_account.chat_id
                )
            )
            notification.is_sent = True
            notification.save()
        except Exception as e:
            print(f"Error sending notification: {str(e)}")

        return notification

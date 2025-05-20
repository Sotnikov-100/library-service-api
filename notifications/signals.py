import asyncio
import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from borrowings.models import Borrowing
from notifications.models import Notification
from notifications.tasks import create_notification_task, send_notification_task
from notifications.telegram_bot import TelegramNotification
from payments.models import Payment
from tgaccounts.models import TelegramAccount

logger = logging.getLogger(__name__)


async def send_telegram_message(chat_id, message):
    """Helper function to send Telegram message and create notification record."""
    notifier = TelegramNotification()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    success = loop.run_until_complete(
        notifier.send_notification(message=message, chat_id=chat_id)
    )
    return success


@receiver([post_save, post_delete], sender=TelegramAccount)
def telegram_account_receiver(sender, instance, **kwargs):
    """Handle Telegram account events."""
    try:
        if kwargs.get("signal") == post_save:
            if kwargs.get("created"):
                # Send welcome message directly
                notifier = TelegramNotification()
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                message = f"🎉 Welcome! Your Telegram account has been successfully linked to {instance.user.email}.\nYour bind token: {instance.bind_token}"
                success = loop.run_until_complete(
                    notifier.send_notification(
                        message=message,
                        chat_id=instance.chat_id,
                    )
                )

                # Create notification record with correct status
                if success:
                    Notification.objects.create(
                        user=instance.user, message=message, is_sent=True
                    )
            else:
                # Send update message directly
                notifier = TelegramNotification()
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                message = f"📱 Your Telegram account has been updated for {instance.user.email}.\nYour bind token: {instance.bind_token}"
                success = loop.run_until_complete(
                    notifier.send_notification(
                        message=message,
                        chat_id=instance.chat_id,
                    )
                )

                # Create notification record with correct status
                if success:
                    Notification.objects.create(
                        user=instance.user, message=message, is_sent=True
                    )
        elif kwargs.get("signal") == post_delete:
            # Send notification for API deletions
            notifier = TelegramNotification()
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            message = f"👋 Your Telegram account has been unlinked from {instance.user.email}. You will no longer receive notifications."
            success = loop.run_until_complete(
                notifier.send_notification(
                    message=message,
                    chat_id=instance.chat_id,
                )
            )

            # Create notification record with correct status
            if success:
                Notification.objects.create(
                    user=instance.user, message=message, is_sent=True
                )
    except Exception as e:
        logger.error(f"Critical error in telegram_account_receiver: {str(e)}")


@receiver(post_save, sender=Borrowing)
def borrowing_post_save(sender, instance, created, **kwargs):
    """Handle borrowing events."""
    try:
        if not hasattr(instance.user, "telegram_account"):
            return

        message = (
            f"{'📚 New' if created else '📖 Updated'} borrowing:\n"
            f"Book: {instance.book.title}\n"
            f"Borrow date: {instance.borrow_date}\n"
            f"Expected return: {instance.expected_return_date}"
        )
        create_notification_task.delay(instance.user.id, message)

    except Exception as e:
        logger.error(f"Critical error in borrowing_post_save: {str(e)}")


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    try:
        user = instance.borrowing.user
        if not hasattr(user, "telegram_account"):
            return

        message = (
            f"{'💰 New' if created else '💳 Updated'} payment:\n"
            f"Amount: ${instance.money_to_pay}\n"
            f"Status: {instance.status}\n"
            f"Type: {instance.type}\n"
            f"For book: {instance.borrowing.book.title}"
        )

        notification = Notification.objects.create(
            user=user, message=message, is_sent=False
        )
        send_notification_task.delay(notification.id)

    except Exception as e:
        logger.error(f"Error in payment_post_save: {str(e)}")

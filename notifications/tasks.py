import asyncio
import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction

from notifications.models import Notification
from notifications.telegram_bot import TelegramNotification, TelegramNotificationService
from tgaccounts.models import TelegramAccount

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def check_telegram_account_task(chat_id):
    """Check if Telegram account exists."""
    try:
        account = TelegramAccount.objects.get(chat_id=chat_id)
        return {"exists": True, "username": account.user.username or account.user.email}
    except TelegramAccount.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Critical error checking telegram account: {str(e)}")
        return None


@shared_task(bind=True, max_retries=3)
def send_notification_task(self, notification_id):
    """Send notification to user through Telegram."""
    service = TelegramNotificationService()
    try:
        notification = Notification.objects.get(id=notification_id)

        if not hasattr(notification.user, "telegram_account"):
            return False

        success = service.send(
            message=notification.message,
            chat_id=notification.user.telegram_account.chat_id,
        )

        if success:
            notification.is_sent = True
            notification.save()
        else:
            self.retry(countdown=60 * 5)

        return success
    except Notification.DoesNotExist:
        return False
    except Exception as e:
        logger.error(f"Critical error sending notification: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)


@shared_task
def send_notification_to_all_users(message, chat_id=None):
    """Send broadcast message to all users with Telegram accounts."""
    service = TelegramNotificationService()
    if chat_id:
        user_id = User.objects.filter(is_staff=True).values_list('id', flat=True).first()
        service.send(message=message, chat_id=chat_id)
        Notification.objects.create(user_id=user_id, message=message, is_sent=True)
    try:
        users = User.objects.filter(telegram_account__isnull=False)
        notification_count = 0

        for user in users:
            success = service.send(
                message=message,
                chat_id=user.telegram_account.chat_id,
            )

            if success:
                Notification.objects.create(user=user, message=message, is_sent=True)
                notification_count += 1

        return notification_count
    except Exception as e:
        logger.error(f"Critical error sending broadcast: {str(e)}")
        return 0


@shared_task(bind=True, max_retries=3)
def create_telegram_account_task(self, email, chat_id):
    """Create Telegram account for user."""
    service = TelegramNotificationService()
    try:
        with transaction.atomic():
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                message = (
                    "⚠️ User with this email is not registered in our system.\n\n"
                    "Please register first at our website:\n"
                    "http://127.0.0.1/api/v1/users/register/\n\n"
                    "After registration, you can link your Telegram account."
                )
                service.send(message=message, chat_id=chat_id, )
                return False

            if TelegramAccount.objects.filter(chat_id=chat_id).exists():
                # Send notification directly for already linked account
                message = "⚠️ This Telegram account is already linked to another user."
                service.send(message=message, chat_id=chat_id)
                return False

            # Create account and let signal handle the notification
            TelegramAccount.objects.create(user=user, chat_id=chat_id)
            return True
    except Exception as e:
        logger.error(f"Critical error creating telegram account: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)


@shared_task(bind=True, max_retries=3)
def delete_telegram_account_task(self, chat_id):
    """Delete Telegram account."""
    service = TelegramNotificationService()
    try:
        with transaction.atomic():
            try:
                account = TelegramAccount.objects.get(chat_id=chat_id)
            except TelegramAccount.DoesNotExist:
                message = "ℹ️ You don’t have a linked Telegram account."
                service.send(message=message, chat_id=chat_id)
                return False

            user = account.user

            # Send notification directly through bot before deletion
            message = (
                f"👋 Your Telegram account has been unlinked from {user.email}. "
                "You will no longer receive notifications."
            )
            success = service.send(message=message, chat_id=chat_id)

            # Create notification record with correct status
            if success:
                Notification.objects.create(user=user, message=message, is_sent=True)

            # Delete the account
            account.delete()
            return True
    except Exception as e:
        logger.error(f"Critical error deleting telegram account: {str(e)}")
        self.retry(exc=e, countdown=60 * 5)


@shared_task
def create_notification_task(user_id, message):
    """Create and send a notification for regular events."""
    service = TelegramNotificationService()
    try:
        user = User.objects.get(id=user_id)
        if not hasattr(user, "telegram_account"):
            return False

        success = service.send(
            message=message,
            chat_id=user.telegram_account.chat_id,
        )

        # Only create notification record if message was sent
        if success:
            Notification.objects.create(user=user, message=message, is_sent=True)
            return True
        return False
    except Exception as e:
        logger.error(f"Critical error creating notification: {str(e)}")
        return False


@shared_task
def check_user_exists_task(email):
    """Check if user exists by email."""
    try:
        user = User.objects.get(email=email)
        return {"exists": True, "username": user.username or user.email}
    except User.DoesNotExist:
        return {"exists": False}
    except Exception as e:
        logger.error(f"Critical error checking user: {str(e)}")
        return {"exists": False, "error": str(e)}


@shared_task
def cleanup_old_notifications():
    """Remove notifications older than 30 days."""
    try:
        from datetime import timedelta

        from django.utils import timezone

        # Delete notifications older than 30 days
        old_date = timezone.now() - timedelta(days=30)
        deleted_count = Notification.objects.filter(created_at__lt=old_date).delete()[0]
        return deleted_count
    except Exception as e:
        logger.error(f"Critical error cleaning up notifications: {str(e)}")
        return 0

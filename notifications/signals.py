import logging

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from borrowings.models import Borrowing
from notifications.models import Notification
from notifications.tasks import create_notification_task, send_notification_task
from payments.models import Payment
from tgaccounts.models import TelegramAccount

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TelegramAccount)
def telegram_account_post_save(sender, instance, created, **kwargs):
    """Handle creation or update of TelegramAccount: send welcome/update message via Celery."""
    try:
        if created:
            message = (
                f"🎉 Welcome! Your Telegram account has been successfully linked to {instance.user.email}.\n"
                f"Your bind token: {instance.bind_token}"
            )
        else:
            message = (
                f"Your Telegram account has been updated for {instance.user.email}.\n"
                f"Your bind token: {instance.bind_token}"
            )

        create_notification_task.delay(instance.user.id, message)

    except Exception as e:
        logger.error(f"Critical error in telegram_account_post_save: {str(e)}")


@receiver(pre_delete, sender=TelegramAccount)
def telegram_account_pre_delete(sender, instance, **kwargs):
    try:
        message = (
            f"Your Telegram account has been unlinked from {instance.user.email}. "
            "You will no longer receive notifications."
        )
        create_notification_task.delay(instance.user.id, message)
    except Exception as e:
        logger.error(f"Critical error in telegram_account_pre_delete: {str(e)}")


@receiver(post_save, sender=Borrowing)
def borrowing_post_save(sender, instance, created, **kwargs):
    """Handle borrowing creation/update: send notification via Celery."""
    try:
        telegram_account = getattr(instance.user, "telegram_account", None)
        if not telegram_account:
            return

        message = (
            f"{'New' if created else 'Updated'} borrowing:\n"
            f"First name: {instance.user.first_name} last Name: {instance.user.last_name}\n"
            f"Book: {instance.book.title}\n"
            f"Borrow date: {instance.borrow_date}\n"
            f"Expected return: {instance.expected_return_date}\n"
            f"Actual return: {instance.actual_return_date}\n"
        )
        create_notification_task.delay(instance.user.id, message)

    except Exception as e:
        logger.error(f"Critical error in borrowing_post_save: {str(e)}")


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Handle payment creation/update: send notification via Celery."""
    try:
        user = instance.borrowing.user
        telegram_account = getattr(user, "telegram_account", None)
        if not telegram_account:
            return

        message = (
            f"{'New' if created else '💳 Updated'} payment:\n"
            f"Amount: ${instance.money_to_pay}\n"
            f"Status: {instance.status}\n"
            f"Type: {instance.type}\n"
            f"session_url: {instance.session_url}\n"
            f"For book: {instance.borrowing.book.title}\n"
            f"money to pay: {instance.money_to_pay}\n"
            f"created at: {instance.created_at}\n"
        )

        notification = Notification.objects.create(
            user=user, message=message, is_sent=False
        )
        send_notification_task.delay(notification.id)

    except Exception as e:
        logger.error(f"Critical error in payment_post_save: {str(e)}")
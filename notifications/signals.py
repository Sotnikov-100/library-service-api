from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from notifications.telegram_bot import TGNotificationService
from tgaccounts.models import TelegramAccount


# @receiver(post_save, sender=Borrowing)
# def borrowing_post_save(sender, instance, created, **kwargs):
#     service = TGNotificationService()
#     if created:
#         message = f"new borrowing: {instance}"
#     else:
#         message = f"borrowing renew: {instance}"
#     service.create_notification(instance.user, message, instance.telegram_account.chat_id)
#
#
# @receiver(post_save, sender=Payment)
# def payment_post_save(sender, instance, created, **kwargs):
#     service = TGNotificationService()
#     if created:
#         message = f"New Payment: {instance}"
#     else:
#         message = f"Payment Renew: {instance}"
#     service.create_notification(instance.user, message, instance.telegram_account.chat_id)

@receiver([post_save, post_delete], sender=TelegramAccount)
def telegram_account_receiver(sender, instance, **kwargs):
    service = TGNotificationService()
    if kwargs.get("signal") == post_save:
        created = kwargs.get("created", None)
        if created:
            message = f"New Telegram Account: Email: {instance.user.email}"
        else:
            message = f"Telegram Account Renew: {instance}"
    else:  # post_delete
        message = f"Telegram Account Deleted: Email: {instance.user.email}"
    service.create_notification(instance.user, message, instance.chat_id)

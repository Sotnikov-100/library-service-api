from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.telegram_bot import NotificationService


@receiver(post_save, sender=Borrowing)
def borrowing_post_save(sender, instance, created, **kwargs):
    service = NotificationService()
    if created:
        message = f"new borrowing: {instance}"
    else:
        message = f"borrowing renew: {instance}"
    service.create_notification(instance.user, message)


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    service = NotificationService()
    if created:
        message = f"New Payment: {instance}"
    else:
        message = f"Payment Renew: {instance}"
    service.create_notification(instance.user, message)
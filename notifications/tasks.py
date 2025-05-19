from celery import shared_task
from django.contrib.auth import get_user_model

from notifications.telegram_bot import TelegramNotification

User = get_user_model()


@shared_task
def send_notification_task(user_id, message, chat_id):
    user = User.objects.get(id=user_id)
    notifier = TelegramNotification()
    notifier.send_notification(message, chat_id)

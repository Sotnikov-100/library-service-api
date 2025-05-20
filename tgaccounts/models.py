import uuid

from django.db import models

from config import settings


class TelegramAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_account",
    )
    chat_id = models.CharField(max_length=255, unique=True)
    bind_token = models.CharField(
        max_length=64, unique=True, default=uuid.uuid4, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.chat_id}"

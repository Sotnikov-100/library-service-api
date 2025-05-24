from django.contrib import admin

from tgaccounts.models import TelegramAccount


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "chat_id", "bind_token", "created_at")
    search_fields = ("user__username", "chat_id", "bind_token")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

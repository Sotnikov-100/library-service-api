from django.urls import path, include

from notifications.views import TelegramBotJoinLinkView

app_name = "notifications"

urlpatterns = [
    path("get-telegram-link/", TelegramBotJoinLinkView.as_view()),
]

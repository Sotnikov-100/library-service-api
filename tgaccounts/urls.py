from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tgaccounts.views import (
    TgBotLinkView,
    TelegramAccountViewSet,
    TelegramAccountRegisterView
)

app_name = "tgaccounts"

router = DefaultRouter()
router.register("tg-accounts", TelegramAccountViewSet, basename="tg-accounts")

urlpatterns = [
    path("telegram-link/", TgBotLinkView.as_view(), name="get_telegram_link"),
    path(
        "tg-accounts/<str:chat_id>/register/",
        TelegramAccountRegisterView.as_view(),
        name="tg_account_register"
    ),
    path("", include(router.urls), name="tg_accounts"),
]

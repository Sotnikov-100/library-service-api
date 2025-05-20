from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.generics import CreateAPIView
from base.viewsets import ModelViewSet
from config.settings import TELEGRAM_BOT_NAME
from tgaccounts.models import TelegramAccount
from tgaccounts.serializers import (
    TelegramAccountCreateSerializer,
    TelegramAccountSerializer,
)

BOT_NAME = TELEGRAM_BOT_NAME


class TgBotLinkView(APIView):
    def get(self, request, *args, **kwargs):
        tg_link = f"https://t.me/{BOT_NAME}"
        return Response({"telegram_bot_link": tg_link})


class TelegramAccountViewSet(ModelViewSet):
    queryset = TelegramAccount.objects.prefetch_related("user")
    permission_classes = [IsAuthenticated]
    request_serializer_class = TelegramAccountSerializer
    response_serializer_class = TelegramAccountSerializer

    request_action_serializer_classes = {
        "create": TelegramAccountCreateSerializer,
        "retrieve": TelegramAccountSerializer,
    }

    response_action_serializer_classes = {
        "create": TelegramAccountCreateSerializer,
        "retrieve": TelegramAccountSerializer,
    }

    def get_object(self):
        return self.request.user.telegram_account


class TelegramAccountRegisterView(CreateAPIView):
    request_serializer_class = TelegramAccountCreateSerializer
    response_serializer_class = TelegramAccountCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs.get("chat_id")
        data = request.data.copy()
        data["chat_id"] = chat_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

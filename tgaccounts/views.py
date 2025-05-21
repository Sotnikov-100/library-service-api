from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.generics import CreateAPIView
from base.viewsets import ModelViewSet
from config.settings import TELEGRAM_BOT_NAME
from tgaccounts.docs import(
    get_create_tg_account_schema,
    get_retrieve_tg_account_schema,
    get_tg_link_schema
)
from tgaccounts.models import TelegramAccount
from tgaccounts.serializers import (
    TelegramAccountCreateSerializer,
    TelegramAccountSerializer,
)

BOT_NAME = TELEGRAM_BOT_NAME


class TgBotLinkView(APIView):
    """
    Returns the Telegram bot link.
    """

    @get_tg_link_schema()
    def get(self, request, *args, **kwargs):
        tg_link = f"https://t.me/{BOT_NAME}"
        return Response({"telegram_bot_link": tg_link})


class TelegramAccountViewSet(ModelViewSet):
    """
    ViewSet for managing the authenticated user's Telegram account.
    Only authenticated users can access.
    """

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
        try:
            return self.request.user.telegram_account
        except TelegramAccount.DoesNotExist:
            raise NotFound("Telegram account not found for this user.")

    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @get_retrieve_tg_account_schema()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TelegramAccountRegisterView(CreateAPIView):
    """
    Registers an account(on the website) for the current user on Telegram.
    """

    request_serializer_class = TelegramAccountCreateSerializer
    response_serializer_class = TelegramAccountCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(exclude=True)
    def post(self, request, *args, **kwargs):
        chat_id = self.kwargs.get("chat_id")
        data = request.data.copy()
        data["chat_id"] = chat_id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from drf_spectacular.utils import OpenApiExample, extend_schema
from tgaccounts.serializers import TelegramAccountCreateSerializer


def get_tg_link_schema():
    return extend_schema(
        summary="Get Telegram bot link",
        description="Returns the URL link to connect with Telegram bot",
    )

def get_retrieve_tg_account_schema():
    return extend_schema(
        summary="Retrieve Telegram account",
        description="Get authenticated user's Telegram account details",
        examples=[
            OpenApiExample(
                "Example response",
                value={
                    "id": 1,
                    "chat_id": "123456789",
                    "bind_token": "a1b2c3d4-e5f6-7890",
                    "created_at": "2023-01-01T12:00:00",
                    "updated_at": "2023-01-01T12:00:00"
                }
            )
        ]
    )

def get_create_tg_account_schema():
    return extend_schema(
        summary="Create Telegram account",
        description="Connect Telegram account to your profile",
        request=TelegramAccountCreateSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value={"chat_id": "123456789"},
                request_only=True
            )
        ]
    )

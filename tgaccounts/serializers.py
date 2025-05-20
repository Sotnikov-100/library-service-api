from rest_framework import serializers

from tgaccounts.models import TelegramAccount
from users.serializers import UserSerializer


class TelegramAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TelegramAccount
        fields = ["id", "user", "chat_id", "bind_token", "created_at", "updated_at"]
        read_only_fields = ("id", "chat_id", "bind_token", "created_at", "updated_at",)


class TelegramAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramAccount
        fields = ["chat_id"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)

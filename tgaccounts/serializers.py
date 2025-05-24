from rest_framework import serializers

from tgaccounts.models import TelegramAccount
from users.serializers import UserSerializer


class TelegramAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TelegramAccount
        fields = ["id", "user", "chat_id", "bind_token", "created_at", "updated_at"]
        read_only_fields = (
            "id",
            "chat_id",
            "bind_token",
            "created_at",
            "updated_at",
        )


class TelegramAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramAccount
        fields = ["chat_id"]

    def validate(self, attrs):
        user = self.context["request"].user
        if TelegramAccount.objects.filter(user=user).exists():
            raise serializers.ValidationError({"user": "User already has a Telegram account"})
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

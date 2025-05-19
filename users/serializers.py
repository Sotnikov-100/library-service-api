from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
            "profile_image"
        )
        read_only_fields = (
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
        )
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "profile_image": {
                "required": False,
                "allow_null": True,
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

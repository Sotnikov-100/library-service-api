from rest_framework import serializers
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "borrowing",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
        ]
        read_only_fields = [
            "status",
            "session_url",
            "session_id",
            "created_at",
            "type",
            "money_to_pay",
        ]

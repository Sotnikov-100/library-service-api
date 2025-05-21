from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from payments.models import Payment, PaymentStatus
from payments.services import create_payment_with_stripe_session, create_fine_payment


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    def validate(self, attrs):
        if attrs["expected_return_date"] <= attrs["borrow_date"]:
            raise ValidationError(
                {
                    "expected_return_date": "Expected return date must "
                    "be greater than borrow date."
                }
            )
        return attrs

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user_id",
            "book_id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
            "book",
        )
        ordering = ["-actual_return_date", "-borrow_date"]

class BorrowingCreateSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        many=False,
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
        )

    @transaction.atomic
    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save(update_fields=["inventory"])
        
        # Add user to validated_data
        validated_data["user"] = self.context["request"].user
        borrowing = Borrowing.objects.create(**validated_data)
        
        # Create payment with Stripe session in one transaction
        create_payment_with_stripe_session(borrowing, self.context["request"])
        
        return borrowing

    def validate(self, attrs):
        if attrs["expected_return_date"] <= attrs["borrow_date"]:
            raise ValidationError(
                {
                    "expected_return_date": "Expected return date must "
                    "be greater than borrow date."
                }
            )

        if attrs["book"].inventory <= 0:
            raise ValidationError(
                {"book inventory": "Book inventory must be greater than 0."}
            )

        user = self.context["request"].user
        if Payment.objects.filter(
            borrowing__user=user, status=PaymentStatus.PENDING
        ).exists():
            raise ValidationError(
                {
                    "pending_payments": "You have pending payments. Cannot create a new borrowing."
                }
            )

        return attrs


class BorrowingReturnUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "actual_return_date",
        )

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise ValidationError("This borrowing has already been required.")
        actual_return_date = attrs.get("actual_return_date")
        if actual_return_date and actual_return_date <= self.instance.borrow_date:
            raise ValidationError(
                {"actual_return_date": "Return date must be after borrow date."}
            )

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data.get(
            "actual_return_date", timezone.now().date()
        )
        instance.book.inventory += 1
        instance.book.save(update_fields=["inventory"])
        instance.save(update_fields=["actual_return_date"])

        # Create fine payment if book is returned late
        if instance.is_expired:
            create_fine_payment(instance, self.context["request"])

        return instance


class BorrowingRetrieveSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    expired_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "book_title",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
            "is_expired",
            "expired_days",
        ]
        read_only_fields = ["id", "user", "book"]

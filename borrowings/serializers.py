from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if attrs["expected_return_date"] <=attrs["borrow_date"]:
            raise ValidationError({
                "expected_return_date": "Expected return date must "
                "be greater than borrow date."
            })
        return attrs

    class Meta:
        model = Borrowing
        fields = (
            # "book",
            "id",
            "user_id",
            "book_id",
            "borrow_date",
            "expected_return_date"
        )

class BorrowingListSerializer(BorrowingSerializer):
    pass


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
        borrowing = Borrowing.objects.create(**validated_data)
        return borrowing

    def validate(self, attrs):
        if attrs["expected_return_date"] <=attrs["borrow_date"]:
            raise ValidationError({
                "expected_return_date": "Expected return date must "
                "be greater than borrow date."
            })

        if attrs["book"].inventory <= 0:
            raise ValidationError({
                "book inventory": "Book inventory must be greater than 0."
            })

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
            raise ValidationError({
                "actual_return_date": "Return date must be after borrow date."
            })

        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data.get("actual_return_date", timezone.now().date())
        instance.book.inventory += 1
        instance.book.save(update_fields=["inventory"])
        instance.save(update_fields=["actual_return_date"])

        return instance

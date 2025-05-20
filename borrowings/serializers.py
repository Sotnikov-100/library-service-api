from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    # book = BookSerializer(read_only=True, many=False)
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
        # book = validated_data.pop("book")
        # book.inventory = book.inventory - 1
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

        # if (
        #     attrs["actual_return_date"]
        # ):
        #     raise ValidationError({
        #         "actual_return_date": "Actual return date shoutd not be filled in creation."
        #     })
        #
        # if (
        #     attrs["actual_return_date"] <= attrs["borrow_date"]
        # ):
        #     raise ValidationError({
        #         "actual_return_date": "If actual return date exists it "
        #                               "must be greater than borrow date."
        #     })

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    # book = BookSerializer(read_only=True, many=False)
    # def validate(self, attrs):
    #     if attrs["expected_return_date"] <=attrs["borrow_date"]:
    #         raise ValidationError({
    #             "expected_return_date": "Expected return date must "
    #             "be greater than borrow date."
    #         })
    #     if (
    #         attrs["actual_return_date"] is not None
    #         and attrs["actual_return_date"] <= attrs["borrow_date"]
    #     ):
    #         raise ValidationError({
    #             "actual_return_date": "If actual return date exists it "
    #                                   "must be greater than borrow date."
    #         })

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
    # books = serializers.SlugRelatedField(
    #     slug_field="title",
    #     many=False,
    #     read_only=True,
    # )
    # class Meta:
    #     model = Borrowing
    #     fields = (
    #         "id",
    #         "books",
    #         "user_id",
    #         "book_id",
    #         "borrow_date",
    #         "expected_return_date",
    #         "actual_return_date",
    #     )

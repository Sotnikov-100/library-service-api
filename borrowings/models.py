from datetime import datetime

from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book
from config import settings


class Borrowing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="books")
    borrow_date = models.DateField(null=False, blank=False)
    expected_return_date = models.DateField(null=False, blank=False)
    actual_return_date = models.DateField(null=True, blank=True)

    def clean(self: "Borrowing") -> None:
        if self.expected_return_date <= self.borrow_date:
            raise ValidationError({
                "expected_return_date": "Expected return date must "
                "be greater than borrow date."
            })
        if (
            self.actual_return_date is not None
            and self.actual_return_date <= self.borrow_date
        ):
            raise ValidationError({
                "actual_return_date": "If actual return date exists it "
                                      "must be greater than borrow date."
            })

    @property
    def is_active(self: "Borrowing") -> bool:
        return self.actual_return_date is None

    @property
    def is_expired(self: "Borrowing") -> bool:
        return self.actual_return_date > datetime.date.today()

    class Meta:
        ordering = ["-actual_return_date", "expected_return_date"]
        verbose_name_plural = "borrowings"

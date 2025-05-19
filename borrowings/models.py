from django.db import models

from config import settings


class Borrowing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    borrow_date = models.DateField(null=False, blank=False)
    expected_return_date = models.DateField(null=False, blank=False)
    actual_return_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        return self.actual_return_date is None

    class Meta:
        ordering = ["actual_return_date", "expected_return_date"]
        verbose_name_plural = "borrowings"

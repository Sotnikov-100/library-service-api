from django.db import models
from django.utils.translation import gettext_lazy as _
# from borrowings.models import Borrowing


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    PAID = "PAID", _("Paid")


class PaymentType(models.TextChoices):
    PAYMENT = "PAYMENT", _("Payment")
    FINE = "FINE", _("Fine")


class Payment(models.Model):
    borrowing = models.ForeignKey(
        "Borrowing",
        on_delete=models.PROTECT,
        related_name="payments"
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.PAYMENT
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.borrowing.user.email} - {self.type} - {self.status}"

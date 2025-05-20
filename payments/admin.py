from django.contrib import admin
from payments.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "borrowing",
        "status",
        "type",
        "money_to_pay",
        "created_at",
    )
    list_filter = ("status", "type", "created_at")
    search_fields = ("borrowing__user__email", "session_id")
    ordering = ("-created_at",)

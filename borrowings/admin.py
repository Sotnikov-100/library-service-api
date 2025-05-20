from django.contrib import admin

from borrowings.models import Borrowing


@admin.register(Borrowing)
class Borrowing(admin.ModelAdmin):
    list_display = ("user", "book", "created_at", "borrow_date", "expected_return_date", "actual_return_date")
    search_fields = ("user", "book", "borrow_date", "expected_return_date")
    list_filter = ("user","book", "borrow_date", "expected_return_date")

from django.contrib import admin

from authors.models import BookAuthor
from books.models import Book


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1
    can_delete = False
    autocomplete_fields = ["author"]


@admin.register(Book)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("title", "cover", "inventory", "daily_fee", "image")
    search_fields = ("title",)
    list_filter = ("title", "inventory", "authors")
    inlines = (BookAuthorInline,)

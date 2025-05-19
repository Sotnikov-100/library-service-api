from django.contrib import admin
from authors.models import Author, BookAuthor


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "birth_date")
    search_fields = ("first_name", "last_name")
    list_filter = ("birth_date",)


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ("book", "author")
    search_fields = ("book__title", "author__first_name", "author__last_name")

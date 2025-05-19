import os
import uuid
from enum import unique

from django.db import models
from django.utils.text import slugify
from authors.models import Author, BookAuthor


def book_image_file_path(instance: "Book", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("books/", filename)

@unique
class BookCoverType(models.TextChoices):
    HARD = "Hard", "Hardcover"
    SOFT = "Soft", "Softcover"


class Book(models.Model):
    title = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=BookCoverType.choices, default=BookCoverType.HARD)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to=book_image_file_path)
    authors = models.ManyToManyField("Author", through="BookAuthor", related_name="books")

    def __str__(self) -> str:
        return self.title

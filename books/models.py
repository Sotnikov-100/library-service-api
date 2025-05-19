import os
import uuid

from django.db import models
from django.utils.text import slugify


def book_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("books/", filename)


class Book(models.Model):
    title = models.CharField(max_length=255)
    cover = models.CharField(max_length=4)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to=book_image_file_path)
    authors = models.ManyToManyField("Author", through="BookAuthor", related_name="books")

    def __str__(self):
        return self.title
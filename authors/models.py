from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to="authors/", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class BookAuthor(models.Model):
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="book_authors")
    author = models.ForeignKey("Author", on_delete=models.CASCADE, related_name="author_books")

    class Meta:
        unique_together = ("book", "author")
        indexes = [
            models.Index(fields=["book", "author"]),
        ]

    def __str__(self):
        return f"{self.author} -> {self.book}"

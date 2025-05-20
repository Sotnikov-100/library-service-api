from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from authors.models import Author, BookAuthor
from books.models import Book
from authors.serializers import AuthorSerializer

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(read_only=True, many=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "inventory",
            "cover",
            "daily_fee",
            "authors"
        )


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        many=True,
    )
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "inventory",
            "cover",
            "daily_fee",
            "authors"
        )

    def validate_daily_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Daily Fee must be greater than 0")
        return value

    def validate_inventory(self, value):
        if value < 0:
            raise serializers.ValidationError("Inventory must be greater than 0")
        return value

    def create(self, validated_data):
        authors = validated_data.pop("authors")
        book = Book.objects.create(**validated_data)
        for author in authors:
            BookAuthor.objects.create(book=book, author=author)
        return book

    def update(self, instance, validated_data):
        authors = validated_data.pop("authors", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if authors is not None:
            instance.authors.clear()
            for author in authors:
                BookAuthor.objects.create(book=instance, author=author)

        return instance

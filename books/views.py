from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from books.models import Book
from books.serializers import BookCreateUpdateSerializer, BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    admin_actions = {"create", "update", "partial_update", "destroy"}

    def get_serializer_class(self):
        if self.action in self.admin_actions:
            return BookCreateUpdateSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in self.admin_actions:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

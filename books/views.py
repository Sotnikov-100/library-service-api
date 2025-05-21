from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from books.docs import(
    get_book_create_schema,
    get_book_delete_schema,
    get_book_list_schema,
    get_book_partial_update_schema,
    get_book_retrieve_schema,
    get_book_update_schema
)

from books.models import Book
from books.serializers import BookCreateUpdateSerializer, BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
     **BookViewSet** allows performing CRUD operations on Book objects.

     **Access Control:**

     - "list", "retrieve" - available to all users.
     - "create", "update", "partial_update", "destroy" - available only to administrators.

    **Serializers:**

    - For creation/editing: "BookCreateUpdateSerializer"
    - For view: "BookListSerializer"
    """

    queryset = Book.objects.all()

    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "authors__first_name", "authors__last_name"]

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


    @get_book_list_schema()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @get_book_create_schema()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @get_book_retrieve_schema()
    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @get_book_update_schema()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @get_book_partial_update_schema()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @get_book_delete_schema()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

from rest_framework import viewsets, permissions

from authors.docs import get_author_create_schema, get_author_delete_schema, get_author_list_schema, \
    get_author_partial_update_schema, \
    get_author_retrieve_schema, get_author_update_schema
from authors.models import Author
from authors.serializers import AuthorSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """
     **AuthorViewSet** allows performing CRUD operations on Author objects.

     **Access Control:**

     - "list", "retrieve" - available to all users.
     - "create", "update", "partial_update", "destroy" - available only to administrators.
    """

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @get_author_list_schema()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @get_author_create_schema()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @get_author_retrieve_schema()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @get_author_update_schema()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @get_author_partial_update_schema()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @get_author_delete_schema()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

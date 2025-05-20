from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from borrowings.models import Borrowing
from borrowings.pagiantion import BorrowingSetPagination
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnUpdateSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    pagination_class = BorrowingSetPagination

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = BorrowingListSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action in ("update", "partial_update"):
            return BorrowingReturnUpdateSerializer

        return serializer

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = BorrowingReturnUpdateSerializer(
            borrowing,
            data={},
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

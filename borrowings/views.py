from rest_framework import viewsets

from borrowings.models import Borrowing
from borrowings.pagiantion import BorrowingSetPagination
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingCreateSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
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

        if self.action is "create":
            return BorrowingCreateSerializer

        if self.action is ["update", "partial_update"]:
            return BorrowingUpdateSerializer

        return serializer
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

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id", None)
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active", None)
        if is_active:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = BorrowingListSerializer

        if self.action is "create":
            return BorrowingCreateSerializer

        return serializer
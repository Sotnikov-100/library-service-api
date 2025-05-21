from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import BooleanField, ExpressionWrapper, Q

from borrowings.models import Borrowing
from borrowings.pagiantion import BorrowingSetPagination
from borrowings.permissions import IsAuthenticatedOnly
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnUpdateSerializer,
    BorrowingRetrieveSerializer,
)
from borrowings.docs import(
    get_borrowings_create_schema,
    get_borrowings_delete_schema,
    get_borrowings_list_schema,
    get_borrowings_partial_update_schema,
    get_borrowings_retrieve_schema
)


class BorrowingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows borrowings to be viewed or edited.

    ***Access:***

    - Regular users see their own borrowings.
    - Staff users: see all borrowings and can filter them by id.

    """

    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    pagination_class = BorrowingSetPagination
    permission_classes = (IsAuthenticatedOnly,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Borrowing.objects.none()

        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id", None)
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        queryset = queryset.annotate(
            is_active_calc=ExpressionWrapper(
                Q(actual_return_date__isnull=True),
                output_field=BooleanField()
            )
        )

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(is_active_calc=is_active)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer

        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action in ("update", "partial_update"):
            return BorrowingReturnUpdateSerializer

        if self.action == "retrieve":
            return BorrowingRetrieveSerializer
        return self.serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @extend_schema(exclude=True)
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

    @get_borrowings_list_schema()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @get_borrowings_create_schema()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @get_borrowings_retrieve_schema()
    def retrieve(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @get_borrowings_partial_update_schema()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @get_borrowings_delete_schema()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

import os

import stripe

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from base.viewsets import ModelViewSet
from notifications.telegram_bot import TelegramNotificationService
from payments.models import Payment, PaymentStatus
from payments.permissions import IsAdminOrOwner
from payments.serializers import PaymentSerializer, PaymentCreateSerializer
from payments.services import create_payment_with_stripe_session, create_stripe_session

from payments.docs import (
    get_payments_cancel_schema,
    get_payments_create_schema,
    get_payments_list_schema,
    get_payments_retrieve_schema,
    get_payments_success_schema,
    get_renew_session_schema
)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


class PaymentViewSet(ModelViewSet):
    """
        Handles payment operations related to borrowings.

        ***Permissions: ***

        - Only authenticated users can access.
        - Admins see all payments, regular users see only their own
    """
    queryset = Payment.objects.all().select_related(
        "borrowing__user", "borrowing__book"
    )
    request_serializer_class = PaymentCreateSerializer
    response_serializer_class = PaymentSerializer

    request_action_serializer_classes = {
        "create": PaymentCreateSerializer,
        "list": PaymentCreateSerializer,
    }
    response_action_serializer_classes = {
        "list": PaymentSerializer,
        "create": PaymentSerializer,
    }
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(borrowing__user=user)

    def perform_create(self, serializer):
        payment = serializer.save()
        create_payment_with_stripe_session(payment.borrowing, self.request)
        return payment

    @get_payments_success_schema()
    @action(detail=True, methods=["GET"], url_path="success")
    def payment_success(self, request, pk=None):
        service = TelegramNotificationService()
        payment = self.get_object()
        user_chat_id = payment.borrowing.user.telegram_account.chat_id
        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.payment_status == "paid":
                payment.status = PaymentStatus.PAID
                payment.save()
                message = "Payment completed successfully!"

                service.send(message=message, chat_id=user_chat_id)

                return Response(
                    {"status": "Paid", "message": "Payment successfully complted."},
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"status": "Pending", "message": "Payment is pending. Please wait a moment."},
                status=status.HTTP_202_ACCEPTED,
            )
        except stripe.error.StripeError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @get_payments_cancel_schema()
    @action(detail=True, methods=["GET"], url_path="cancel")
    def payment_cancel(self, request, pk=None):
        return Response(
            {
                "status": "cancelled",
                "message": "Payment was cancelled. You can complete it later.",
                "payment_url": self.get_object().session_url,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Deleting payments is not allowed.")

    @get_renew_session_schema()
    @action(detail=True, methods=["POST"])
    def renew_session(self, request, pk=None):
        payment = self.get_object()
        if payment.status != PaymentStatus.EXPIRED:
            return Response(
                {"error": "Only expired payments can be renewed."}, status=400
            )
        create_stripe_session(payment, request)
        return Response({"session_url": payment.session_url})

    @get_payments_list_schema()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @get_payments_retrieve_schema()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @get_payments_create_schema()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

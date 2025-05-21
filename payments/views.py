import os

import stripe
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from base.viewsets import ModelViewSet
from payments.models import Payment, PaymentStatus
from payments.permissions import IsAdminOrOwner
from payments.serializers import PaymentSerializer, PaymentCreateSerializer
from payments.services import create_stripe_session, send_telegram_notification, create_payment_with_stripe_session

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


class PaymentViewSet(ModelViewSet):
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

    @action(detail=True, methods=["GET"], url_path="success")
    def payment_success(self, request, pk=None):
        payment = self.get_object()
        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.payment_status == "paid":
                payment.status = PaymentStatus.PAID
                payment.save()
                send_telegram_notification(payment)
                return Response(
                    {"status": "success", "message": "Payment completed successfully!"}
                )
            return Response(
                {"status": "pending", "message": "Payment is still pending."},
                status=status.HTTP_202_ACCEPTED,
            )
        except stripe.error.StripeError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied("Deleting payments is not allowed.")

    @action(detail=True, methods=["POST"])
    def renew_session(self, request, pk=None):
        payment = self.get_object()
        if payment.status != PaymentStatus.EXPIRED:
            return Response(
                {"error": "Only expired payments can be renewed."}, status=400
            )
        create_stripe_session(payment, request)
        return Response({"session_url": payment.session_url})

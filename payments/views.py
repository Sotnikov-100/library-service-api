from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.permissions import IsAdminOrOwner, IsAdminOrReadOnly
from payments.services import create_stripe_session


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated(), IsAdminOrOwner()]
        elif self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        elif self.action == "destroy":
            raise PermissionDenied("Deleting payments is not allowed.")
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)

    def perform_create(self, serializer):
        payment = serializer.save()
        create_stripe_session(payment)

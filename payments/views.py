from rest_framework import generics, permissions
from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.permissions import IsAdminOrOwner


class PaymentListViewSet(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission__classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)


class PaymentDetailViewSet(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

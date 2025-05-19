from django.urls import path, include
from payments.views import PaymentListViewSet, PaymentDetailViewSet


urlpatterns = [
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
]

app_name = "payments"

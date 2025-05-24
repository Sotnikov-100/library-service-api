from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet
from payments.webhooks import stripe_webhook

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payments")

urlpatterns = [
    path("webhook/", stripe_webhook, name="stripe-webhook"),
    path(
        "success/<int:pk>/",
        PaymentViewSet.as_view({"get": "payment_success"}),
        name="payment-success",
    ),
    path(
        "cancel/<int:pk>/",
        PaymentViewSet.as_view({"get": "payment_cancel"}),
        name="payment-cancel",
    ),
    path("", include(router.urls)),
]

app_name = "payments"

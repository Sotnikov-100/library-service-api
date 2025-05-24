import os
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from payments.models import Payment, PaymentStatus
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@shared_task
def check_expired_payments():
    expired_payments = Payment.objects.filter(
        status=PaymentStatus.PENDING,
        created_at__lte=timezone.now() - timedelta(hours=24),
    )

    for payment in expired_payments:
        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.status == "expired":
                payment.status = PaymentStatus.EXPIRED
                payment.save()
        except stripe.error.StripeError:
            continue

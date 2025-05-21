import os
import stripe
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from payments.models import Payment, PaymentStatus
from payments.services import send_telegram_notification

logger = logging.getLogger(__name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if not sig_header:
        logger.error("Missing Stripe-Signature header")
        return HttpResponse("Missing header", status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        logger.info(f"Processing completed session: {session.id}")
        handle_checkout_session(session)

    return HttpResponse(status=200)


def handle_checkout_session(session):
    logger.info(f"Handling session: {session.id} (status: {session.payment_status})")

    try:
        payment = Payment.objects.get(session_id=session.id)
        if session.payment_status == "paid" and payment.status != PaymentStatus.PAID:
            payment.status = PaymentStatus.PAID
            payment.save()
            logger.info(f"Payment {payment.id} marked as PAID")

            if payment.borrowing:
                send_telegram_notification(payment)

    except Payment.DoesNotExist:
        logger.warning(
            f"No Payment found for session {session.id}. Creating test payment."
        )

        payment = Payment.objects.create(
            borrowing=None,
            session_id=session.id,
            session_url=session.url,
            money_to_pay=session.amount_total / 100,
            status=(
                PaymentStatus.PAID
                if session.payment_status == "paid"
                else PaymentStatus.PENDING
            ),
        )
        logger.info(
            f"Test payment created for session {session.id} with status {payment.status}"
        )

    except Exception as e:
        logger.error(
            f"Unexpected error while processing session {session.id}: {str(e)}"
        )

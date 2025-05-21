import os
import stripe
from django.db import transaction
from decimal import Decimal
from django.urls import reverse
import requests
import logging
from borrowings.models import Borrowing
from payments.models import Payment, PaymentType

logger = logging.getLogger(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
FINE_MULTIPLIER = 2


def calc_payment_amount(borrowing: Borrowing) -> Decimal:
    days = (borrowing.expected_return_date - borrowing.borrow_date).days + 1
    return borrowing.book.daily_fee * days


def create_stripe_session(payment: Payment, request):
    logger.info(f"Creating Stripe session for payment ID: {payment.id}")
    success_url = request.build_absolute_uri(
        reverse("payments:payment-success", args=[payment.id])
    )
    cancel_url = request.build_absolute_uri(
        reverse("payments:payment-cancel", args=[payment.id])
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Book rental: {payment.borrowing.book.title}",
                    },
                    "unit_amount": int(payment.money_to_pay * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"payment_id": payment.id},
    )

    payment.session_url = session.url
    payment.session_id = session.id
    payment.save()


@transaction.atomic
def create_payment_for_borrowing(borrowing: Borrowing) -> Payment:
    amount = calc_payment_amount(borrowing)
    payment = Payment.objects.create(
        borrowing=borrowing, money_to_pay=amount, type=PaymentType.PAYMENT
    )
    return payment


@transaction.atomic
def create_fine_payment(borrowing: Borrowing) -> Payment | None:
    if not borrowing.is_expired:
        return None

    fine_amount = borrowing.calculate_fine_amount(FINE_MULTIPLIER)

    payment = Payment.objects.create(
        borrowing=borrowing, money_to_pay=fine_amount, type=PaymentType.FINE
    )
    return payment


def send_telegram_notification(payment: Payment):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    message = (
        f"New payment received!\n"
        f"Type: {payment.get_type_display()}\n"
        f"Amount: {payment.money_to_pay} USD\n"
        f"Book: {payment.borrowing.book.title}\n"
        f"User: {payment.borrowing.user.email}"
    )
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": message},
    )

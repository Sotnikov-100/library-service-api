import os

import requests
import stripe
from django.db import transaction
from decimal import Decimal
from django.urls import reverse
from borrowings.models import Borrowing
from payments.models import Payment, PaymentType

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
FINE_MULTIPLIER = 2

def calc_payment_amount(borrowing: Borrowing) -> Decimal:
    days = (borrowing.expected_return_date - borrowing.borrow_date).days + 1
    return borrowing.book.daily_fee * days

def create_stripe_session(payment: Payment, request) -> None:
    """
    Creates Stripe session for payment and updates payment with session info.
    """
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
                        "name": f"{'Late return fine' if payment.type == PaymentType.FINE else 'Book rental'}: {payment.borrowing.book.title}",
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
def create_payment_with_stripe_session(borrowing: Borrowing, request) -> Payment:
    """
    Creates a payment for borrowing and its Stripe session in one transaction.
    """
    # Create payment
    amount = calc_payment_amount(borrowing)
    payment = Payment.objects.create(
        borrowing=borrowing, money_to_pay=amount, type=PaymentType.PAYMENT
    )

    # Create Stripe session
    create_stripe_session(payment, request)
    return payment

@transaction.atomic
def create_fine_payment(borrowing: Borrowing, request) -> Payment | None:
    """
    Creates a fine payment for late return with Stripe session.
    """
    if not borrowing.is_expired:
        return None

    fine_amount = borrowing.calculate_fine_amount(FINE_MULTIPLIER)
    
    # Create payment
    payment = Payment.objects.create(
        borrowing=borrowing, 
        money_to_pay=fine_amount, 
        type=PaymentType.FINE
    )

    # Create Stripe session
    create_stripe_session(payment, request)
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

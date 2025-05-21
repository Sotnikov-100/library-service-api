from drf_spectacular.utils import OpenApiExample, extend_schema

from payments.serializers import PaymentSerializer


def get_payments_list_schema():
    return extend_schema(
        summary="List all payments",
        description="Get list of payments. Admins see all payments, regular users see only their own.",
        examples=[
            OpenApiExample(
                "Example response",
                value=[{
                    "id": 1,
                    "borrowing": "Borrowing #1",
                    "status": "PENDING",
                    "type": "PAYMENT",
                    "session_url": "https://checkout.stripe.com/session_123",
                    "money_to_pay": "10.00",
                    "created_at": "2023-01-01T12:00:00"
                }],
                response_only=True
            )
        ]
    )

def get_payments_create_schema():
    return extend_schema(
        summary="Create payment",
        request=PaymentSerializer,
        description="Create a new payment for borrowing.",
        examples=[
            OpenApiExample(
                "Payment Creation Request",
                value={
                    "borrowing": 1,
                    "payment_type": "PAYMENT"
                },
                request_only=True,
                description="Standard payment creation payload"
            ),
            OpenApiExample(
                "Successful Response",
                value={
                    "id": "pay_1Nf3Z2KZvQl8Xy2JKqXxY2a3",
                    "status": "PENDING",
                    "type": "PAYMENT",
                    "borrowing": 1,
                    "session_url": "https://checkout.stripe.com/c/pay/cs_test_...",
                    "session_id": "cs_test_abc123",
                    "money_to_pay": "15.99"
                },
                response_only=True,
            )
        ]
)

def get_payments_retrieve_schema():
    return extend_schema(
        summary="Retrieve payment details",
        description="Get detailed information about specific payment.",
        examples=[
            OpenApiExample(
                "Example response",
                value={
                    "id": 1,
                    "borrowing": "1",
                    "status": "PENDING",
                    "type": "PAYMENT",
                    "session_url": "https://checkout.stripe.com/session_123",
                    "money_to_pay": "10.00",
                    "created_at": "2023-01-01T12:00:00"
                },
                response_only=True
            )
        ]
    )

def get_payments_success_schema():
    return extend_schema(
        summary="Payment success",
        description="Endpoint for when payment is successful.",
    )

def get_payments_cancel_schema():
    return extend_schema(
        summary="Payment cancel",
        description="Endpoint for when payment is cancelled.",
    )

def get_renew_session_schema():
    return extend_schema(
        summary="Renew expired payment session",
        description="Create new Stripe session for expired payment.",
    )

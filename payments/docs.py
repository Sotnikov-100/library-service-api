from drf_spectacular.utils import OpenApiExample, extend_schema


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

def get_payments_create_schema():
    return extend_schema(
        summary="Create new payment",
        description="New payment automatically is created when created new borrowing.",
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

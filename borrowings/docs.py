from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiExample, extend_schema
from borrowings.serializers import(
    BorrowingCreateSerializer,
    BorrowingReturnUpdateSerializer,
    BorrowingRetrieveSerializer
)

USER_ID_PARAM = OpenApiParameter(
    name="user_id",
    type=OpenApiTypes.INT,
    description="Filter borrowings by user ID (for admin only)",
    required=False
)

IS_ACTIVE_PARAM = OpenApiParameter(
    name="is_active",
    type=OpenApiTypes.BOOL,
    description="Filter active/inactive (true/false) borrowings",
    required=False
)

BORROWING_EXAMPLE_REQUEST = {
    "book": 1,
    "borrow_date": "2023-01-15",
    "expected_return_date": "2023-01-30"
}

BORROWING_EXAMPLE_RESPONSE = {
    "id": 1,
    "user": 1,
    "book": 1,
    "borrow_date": "2023-01-15",
    "expected_return_date": "2023-01-30",
    "actual_return_date": None,
    "is_active": True
}

BORROWING_RETRIEVE_EXAMPLE = {
    "id": 1,
    "user": 1,
    "book": 1,
    "book_title": "Sample Book",
    "borrow_date": "2023-01-15",
    "expected_return_date": "2023-01-30",
    "actual_return_date": None,
    "is_active": True,
    "is_expired": False,
    "expired_days": 0
}

BORROWING_RETURN_EXAMPLE = {
    "id": 1,
    "actual_return_date": "2023-01-28"
}

def get_borrowings_list_schema():
    return extend_schema(
        summary="List all borrowings",
        description="Get a list of all borrowings. For non-admin users, "
                   "only their own borrowings are returned.",
        parameters=[USER_ID_PARAM, IS_ACTIVE_PARAM],
        examples=[
            OpenApiExample(
                "Example response",
                value=[BORROWING_EXAMPLE_RESPONSE],
                response_only=True
            )
        ]
    )

def get_borrowings_create_schema():
    return extend_schema(
        summary="Create new borrowing",
        description="Create a new borrowing. Decrements book inventory.",
        request=BorrowingCreateSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value=BORROWING_EXAMPLE_REQUEST,
                request_only=True
            ),
            OpenApiExample(
                "Example response",
                value=BORROWING_EXAMPLE_RESPONSE,
                response_only=True
            )
        ]
    )

def get_borrowings_retrieve_schema():
    return extend_schema(
        summary="Retrieve borrowing details",
        description="Get detailed information about specific borrowing.",
        request=BorrowingRetrieveSerializer,
        examples=[
            OpenApiExample(
                "Example response",
                value=BORROWING_RETRIEVE_EXAMPLE,
                response_only=True
            )
        ]
    )

def get_borrowings_partial_update_schema():
    return extend_schema(
        summary="Partial update borrowing",
        description="Update borrowing fields. Mainly used for update the date when book was returned.",
        request=BorrowingReturnUpdateSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value={"actual_return_date": "2023-01-28"},
                request_only=True
            ),
            OpenApiExample(
                "Example response",
                value=BORROWING_RETURN_EXAMPLE,
                response_only=True
            )
        ]
    )

def get_borrowings_delete_schema():
    return extend_schema(
        summary="Delete borrowing",
        description="Delete borrowing. Admin only.",
    )

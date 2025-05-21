from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, OpenApiParameter, OpenApiExample, extend_schema
from books.serializers import BookCreateUpdateSerializer, BookSerializer


SEARCH_PARAMETER = OpenApiParameter(
    name="search",
    type=OpenApiTypes.STR,
    description="Search by title or author name",
    required=False
)

BOOK_EXAMPLE_REQUEST = {
    "title": "Book Title",
    "inventory": 5,
    "cover": "Hard",
    "daily_fee": "5.99",
    "authors": [1, 2]
}

BOOK_EXAMPLE_RESPONSE = {
    "id": 1,
    "title": "Book Title",
    "inventory": 5,
    "cover": "Hard",
    "daily_fee": "5.99",
    "authors": [
        {
            "id": 1,
            "first_name": "Author",
            "last_name": "One"
        }
    ]
}

def get_book_list_schema():
    return extend_schema(
        summary="List all books",
        description="Get a list of all available books with search option.",
        parameters=[
            SEARCH_PARAMETER,
        ],
        examples=[
            OpenApiExample(
                "Example response",
                value={
                    "count": 100,
                    "next": "http://api.example.com/books/?page=2",
                    "previous": None,
                    "results": [BOOK_EXAMPLE_RESPONSE]
                },
                response_only=True
            )
        ],
    )


def get_book_create_schema():
    return extend_schema(
        summary="Create new book",
        description="Create a new book instance. Admin only.",
        request=BookCreateUpdateSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value=BOOK_EXAMPLE_REQUEST,
                request_only=True
            ),
            OpenApiExample(
                "Example response",
                value=BOOK_EXAMPLE_RESPONSE,
                response_only=True
            )
        ],
    )

def get_book_retrieve_schema():
    return extend_schema(
        summary="Retrieve book details",
        description="Get detailed information about specific book.",
        responses={
            200: BookSerializer,
            404: OpenApiResponse(description="Book not found")
        },
        examples=[
            OpenApiExample(
                "Example response",
                value=BOOK_EXAMPLE_RESPONSE,
                response_only=True
            )
        ]
    )

def get_book_update_schema():
    return extend_schema(
        summary="Full book update",
        description="Full update of all book fields. Admin only.",
        request=BookCreateUpdateSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value=BOOK_EXAMPLE_REQUEST,
                request_only=True
            )
        ]
    )

def get_book_partial_update_schema():
    return extend_schema(
        summary="Partial book update",
        description="Update some book fields. Admin only.",
        request=BookCreateUpdateSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value={
                    "title": "Updated Book Title",
                    "daily_fee": "7.99"
                },
                request_only=True
            )
        ]
    )

def get_book_delete_schema():
    return extend_schema(
        summary="Delete book",
        description="Delete book from database. Admin only.",
    )

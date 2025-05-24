from drf_spectacular.utils import OpenApiExample, extend_schema
from authors.serializers import AuthorSerializer


AUTHOR_EXAMPLE_REQUEST = {
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Famous author of many books",
    "birth_date": "1980-01-15",
    "photo": None
}

AUTHOR_EXAMPLE_RESPONSE = {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Famous author of many books",
    "birth_date": "1980-01-15",
    "photo": None
}

def get_author_list_schema():
    return extend_schema(
        summary="List all authors",
        description="Get a list of all available authors.",
        examples=[
            OpenApiExample(
                "Example response",
                value={
                    "count": 50,
                    "next": "http://api.example.com/authors/?page=2",
                    "previous": None,
                    "results": [AUTHOR_EXAMPLE_RESPONSE]
                },
                response_only=True
            )
        ],
    )

def get_author_create_schema():
    return extend_schema(
        summary="Create new author",
        description="Create a new author. Admin only.",
        request=AuthorSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value=AUTHOR_EXAMPLE_REQUEST,
                request_only=True
            ),
            OpenApiExample(
                "Example response",
                value=AUTHOR_EXAMPLE_RESPONSE,
                response_only=True
            )
        ],
    )

def get_author_retrieve_schema():
    return extend_schema(
        summary="Retrieve author details",
        description="Get detailed information about specific author by ID.",
        examples=[
            OpenApiExample(
                "Example response",
                value=AUTHOR_EXAMPLE_RESPONSE,
                response_only=True
            )
        ]
    )

def get_author_update_schema():
    return extend_schema(
        summary="Full author update",
        description="Full update of all author fields. Requires admin privileges.",
        request=AuthorSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value=AUTHOR_EXAMPLE_REQUEST,
                request_only=True
            ),
            OpenApiExample(
                "Example response",
                value=AUTHOR_EXAMPLE_RESPONSE,
                response_only=True
            )
        ]
    )

def get_author_partial_update_schema():
    return extend_schema(
        summary="Partial author update",
        description="Update some author fields. Requires admin privileges.",
        request=AuthorSerializer,
        examples=[
            OpenApiExample(
                "Example request",
                value={
                    "first_name": "UpdatedFirstName",
                    "bio": "New biography text"
                },
                request_only=True
            ),
            OpenApiExample(
                "Example response",
                value={
                    "id": 1,
                    "first_name": "UpdatedFirstName",
                    "last_name": "Doe",
                    "bio": "New biography text",
                    "birth_date": "1980-01-15",
                    "photo": None
                },
                response_only=True
            )
        ]
    )

def get_author_delete_schema():
    return extend_schema(
        summary="Delete author",
        description="Delete author from database. Requires admin privileges.",
    )



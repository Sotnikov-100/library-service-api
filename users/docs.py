from drf_spectacular.utils import OpenApiExample, extend_schema
from users.serializers import UserSerializer


def get_register_user_schema():
    return extend_schema(
        summary="Create new user",
        description="Public endpoint for user registration. Are needed: email, password, first_name, last_name",
        request=UserSerializer,
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "email": "user@example.com",
                    "password": "securepassword123",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                request_only=True
            )
        ]
    )

def get_users_list_schema():
    return extend_schema(
        summary="Get current user profile",
        description="Retrieve details of the authenticated user.",
        examples=[
            OpenApiExample(
                "Response Example",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_staff": False
                }
            )
        ]
    )

def get_user_update_schema():
    return extend_schema(
        summary="Update user profile",
        description="Update all fields of user profile.",
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "first_name": "NewJohn",
                    "last_name": "NewDoe"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "NewJohn",
                    "last_name": "NewDoe",
                    "is_staff": False
                },
                response_only=True
            )
        ]
    )

def get_user_partial_update_schema():
    return extend_schema(
        summary="Partial update user profile",
        description="Update just some fields of user profile.",
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "first_name": "UpdatedJohn"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "UpdatedJohn",
                    "last_name": "Doe",
                    "is_staff": False
                },
                response_only=True
            )
        ]
    )
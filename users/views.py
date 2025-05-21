from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.serializers import UserSerializer
from users.docs import(
    get_register_user_schema,
    get_user_partial_update_schema,
    get_user_update_schema,
    get_users_list_schema
)


class CreateUserView(generics.CreateAPIView):
    """
    Creates a new user with email, password, first name and last name.
    This is a public endpoint (no authentication required)
    """
    serializer_class = UserSerializer

    @get_register_user_schema()
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Allows the authenticated user to retrieve or update their profile.
    """
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @get_users_list_schema()
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @get_user_update_schema()
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @get_user_partial_update_schema()
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

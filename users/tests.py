from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("users:create")
        self.data_user_1 = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "first_name": "Joel",
            "last_name": "Doe",
        }
        self.data_user_2 = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "first_name": "Ellie",
            "last_name": "Doe",
        }

    def test_user_can_register_with_valid_data(self):
        response = self.client.post(self.url, self.data_user_1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="newuser@example.com").exists()
        )

    def test_user_cannot_register_with_missing_fields(self):
        data = self.data_user_1.copy()
        data["email"] = ""
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(first_name="Joel").exists())

    def test_user_cannot_register_with_existing_email(self):
        response = self.client.post(self.url, self.data_user_1)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url, self.data_user_2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(first_name="Ellie").exists())


class UserLoginTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.data_user_1 = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "first_name": "Joel",
            "last_name": "Doe",
        }
        User.objects.create_user(**self.data_user_1)

    def test_user_can_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("users:token_obtain_pair"),
            {
                "email": self.data_user_1["email"],
                "password": self.data_user_1["password"],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_cannot_login_with_invalid_credentials(self):
        response = self.client.post(
            reverse("users:token_obtain_pair"),
            {"email": self.data_user_1["email"], "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_refresh_access_token(self):
        login_response = self.client.post(
            reverse("users:token_obtain_pair"),
            {
                "email": self.data_user_1["email"],
                "password": self.data_user_1["password"],
            },
        )
        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(
            reverse("users:token_refresh"), {"refresh": refresh_token}
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_user_cannot_refresh_access_token_with_invalid_token(self):
        response = self.client.post(
            reverse("users:token_refresh"), {"refresh": "invalidtoken"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ManageUserViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.url = reverse("users:manage")

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
        )

    def test_authenticated_user_can_retrieve_own_profile(self):
        self.authenticate()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_unauthenticated_user_cannot_access_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from authors.models import Author


class AuthorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        cls.author_data = {
            "first_name": "Test",
            "last_name": "Author",
            "bio": "Test bio",
            "birth_date": "2000-01-01",
        }
        cls.author = Author.objects.create(**cls.author_data)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_author(self):
        response = self.client.post(reverse("authors:author-list"), self.author_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)
        self.assertEqual(Author.objects.last().first_name, "Test")

    def test_author_list(self):
        response = self.client.get(reverse("authors:author-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["last_name"], "Author")

    def test_author_detail(self):
        url = reverse("authors:author-detail", kwargs={"pk": self.author.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["bio"], "Test bio")

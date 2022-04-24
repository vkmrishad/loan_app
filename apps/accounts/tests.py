from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token


class AccountTestCase(APITestCase):
    def setUp(self):
        # Init Client
        self.client = APIClient()

        # Create admin user
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin@@password"
        )

        # Create admin token
        self.admin_token = Token.objects.create(user=self.admin)

        # Create user
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="user@@password"
        )

        # Create user token
        self.user_token = Token.objects.create(user=self.user)

    def test_api_register(self):
        """
        Test user registration endpoint
        """
        request = self.client.post(
            "/api/auth/register/",
            {
                "username": "test_user",
                "email": "testuser@example.com",
                "password": "testuser@@password",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response["username"], "test_user")
        self.assertEqual(response["email"], "testuser@example.com")
        self.assertEqual(response["first_name"], "Test")
        self.assertEqual(response["last_name"], "User")

    def test_api_login(self):
        """
        Test user login endpoint (already created accounts)
        """
        # Admin user login
        request = self.client.post(
            "/api/auth/login/",
            {
                "username": "admin",
                "password": "admin@@password",
            },
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["token"], self.admin_token.key)

        # User login
        request = self.client.post(
            "/api/auth/login/",
            {
                "username": "user",
                "password": "user@@password",
            },
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["token"], self.user_token.key)

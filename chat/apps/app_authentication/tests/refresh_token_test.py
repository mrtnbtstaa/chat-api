from django.test import TestCase, SimpleTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status

User = get_user_model()

class CustomTokenRefreshView(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="martin0010",
            password="martin0010"
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.url = reverse('token-refresh')


    def test_refresh_token_success(self):

        """Should return a new refresh token and access token"""

        response = self.client.post(self.url, {
            "refresh": str(self.refresh)
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('access_token', response.data["data"])
        self.assertIn('refresh_token', response.data["data"])


    def test_refresh_token_invalid(self):

        """Should return a 401 Unauthorized for a invalid refresh token"""

        response = self.client.post(self.url, {
            "refresh": "invalid_token"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_missing(self):
        
        """Should return a 400 Bad request for missing a body"""

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)







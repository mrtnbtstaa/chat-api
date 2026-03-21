from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class LoginIntegrationTest(APITestCase):

    def setUp(self):
        self.username = "martin0010"
        self.password = "martin0010"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )

        fake_picture = SimpleUploadedFile("test_image.png", small_gif, content_type="image/png")

        from apps.app_authentication.models import Profile
        Profile.objects.create(user=self.user, picture=fake_picture)

        self.url = reverse('login-obtain-pair')
    

    def test_login_success(self):

        """ Test that a valid user gets a 200 and tokens """
        data = {
            "username": self.username,
            "password": self.password
        }

        response = self.client.post(self.url, data, format='json')

        token = response.data["data"]["tokens"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)      
        self.assertIn('access_token', token)
        self.assertIn('refresh_token', token)


    def test_login_wrong_password(self):
        """Test that wrong credentials return 401 Unauthorized"""
        data = {
            "username": self.username,
            "password": "wrong_password"
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    
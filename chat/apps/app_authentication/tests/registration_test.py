from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from apps.app_authentication.models import Profile 
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

class RegistrationTest(APITestCase):

    
    def generate_photo(self):
        """Generates a dummy image in memory."""
        file = BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.seek(0)
        return SimpleUploadedFile('test_photo.png', file.read(), content_type='image/png')

    def setUp(self):
        self.register_url = reverse('register')
        self.valid_payload = {
            "username": "testuser",
            "password": "martin0010",
            "confirm_password": "martin0010",
        }


    # def test_registration_success(self):

    #     response = self.client.post(self.register_url, self.valid_payload)

    #     # Check status code
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Verify user exists
    #     self.assertTrue(User.objects.filter(username="testuser").exists())

    #     # Verify profile was created and linked
    #     user = User.objects.get(username="testuser")
    #     self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_password_mismatch(self):
        bad_payload = self.valid_payload.copy()
        bad_payload["confirm_password"] = "different_password"

        response = self.client.post(self.register_url, bad_payload)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Password do not match.", str(response.data))

from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework import serializers
from django.db import transaction
from apps.core.utils.validators import is_field_empty
from apps.core.utils.raise_validation import raise_validation
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.exceptions import TokenError

class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    refresh = serializers.CharField(
        blank="Refresh token is required"
    )

    def validate(self, attrs):

        try:

            refresh_token = attrs.get('refresh')

            if is_field_empty(refresh_token):
                raise_validation("Refresh token is required")

            data = super().validate(attrs)

            return {
                "tokens": {
                    "access_token": data["access"],
                    "refresh_token": data["refresh"] 
                }
            }

        except TokenError as e:
            raise_validation("Token has expired or invalid.")
      

class CustomLoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        
        request = self.context.get('request')

        username = attrs.get('username')
        password = attrs.get('password')

        if is_field_empty(username):
            raise_validation("Username is required")

        if is_field_empty(password):
            raise_validation("Password is required")

        user = authenticate(request, username, password)

        if user is None:
            raise_validation("Invalid credentials")

        login(request, user)

        token = self.get_token(user)

        profile = (
            getattr(getattr(user, 'user_profile'), 'picture', None).url
            if getattr(getattr(user, 'user_profile'), 'picture', None)
            else None
        )

        return {
            "user_id": user.id,
            "username": user.username,
            "profile": profile,
            "tokens": {
                "access_token": str(token.access_token),
                "refresh_token": str(token)
            }
        }

    
    # Custom claim added username
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["username"] = user.username

        return token

        




    


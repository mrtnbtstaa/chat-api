from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework import serializers
from django.db import transaction
from apps.core.utils.validators import is_field_empty
from apps.core.utils.helpers import raise_validation
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, Profile

class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    refresh = serializers.CharField(
        allow_null=False,
        error_messages={
            "required": "Refresh token is required",
            "blank": "Refresh token cannot be blank",
            "invalid": "Refresh token is invalid"
        }
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


class RegisterSerializer(serializers.Serializer):

    profile_image = serializers.ImageField(allow_null=True)

    username = serializers.CharField(
        allow_null=False,
        error_messages={
            "required": "Username is required.",
            "blank": "Username cannot be blank.",
            "invalid": "Username is invalid.",
            "null": "Username cannot be null."
        }
    )

    password = serializers.CharField(
        allow_null=False,
        min_length=3,
        error_messages={
            "required": "Password is required.",
            "blank": "Password cannot be blank.",
            "invalid": "Password is invalid.",
            "null": "Password cannot be null.",
            "min_length": "Password must be atleast 8 characters."
        },
    )

    confirm_password = serializers.CharField(
        allow_null=False,
        min_length=3,
        error_messages={
            "required": "Confirm password is required.",
            "blank": "Confirm password cannot be blank.",
            "invalid": "Confirm password is invalid.",
            "null": "Confirm password cannot be null.",
            "min_length": "Confirm password must be atleast 8 characters."
        }
    )

    def validate(self, attrs):


        return super().validate(attrs)
    

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password')
        )

        
        




    


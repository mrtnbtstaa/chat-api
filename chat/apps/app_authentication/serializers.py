from rest_framework import serializers
from django.db import transaction, IntegrityError
from apps.core.utils.validators import is_field_empty
from apps.core.utils.helpers import raise_validation
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from .models import User, Profile
from apps.core.utils.dynamic_char_field import DynamicCharField
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenObtainPairSerializer,
    TokenBlacklistSerializer,
    TokenVerifySerializer
)

class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    refresh = DynamicCharField()

    def validate(self, attrs):

        data = super().validate(attrs)

        return {
            "access_token": data["access"],
            "refresh_token": data["refresh"]
        }
      

class CustomLoginObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        
        request = self.context.get('request')

        email = attrs.get('email')
        password = attrs.get('password')

        if is_field_empty(email):
            raise_validation("Email is required")

        if is_field_empty(password):
            raise_validation("Password is required")

        user = authenticate(request=request, email=email, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials")
        
        login(request, user)

        user.is_online = True
        user.last_login = timezone.now()

        user.save()

        token = self.get_token(user)

        profile = getattr(user, 'user_profile', None)

        if profile and profile.picture:

            try:
                if profile.picture.storage.exists(profile.picture.name):
                    picture_url = profile.picture.url
                else:
                    picture_url = None
            except Exception:
                picture_url = None
        else:
            picture_url = None
        

        return {
            "user_id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "profile": request.build_absolute_uri(picture_url),
            "is_online": user.is_online,
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

    full_name = DynamicCharField()
    email = serializers.EmailField(
        error_messages={
            "required": "Email is required.",
            "null": "Email cannot be null.",
            "blank": "Email cannot be blank.",
            "invalid": "Email is invalid."
        }
    )

    password = DynamicCharField(min_length=8, write_only=True)

    confirm_password = DynamicCharField(min_length=8, write_only=True)

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise_validation(
                key="password",
                message="Passwords do not match."
            )

        return attrs
    

    def create(self, validated_data):
        
        try:
            # Extract confirm password
            validated_data.pop('confirm_password')

            # User creation
            user = User.objects.create_user(**validated_data)

            return user
        
        except IntegrityError:
            raise_validation(
                key="email",
                message="This email is already taken"
            )

class LogoutBlacklistSerializer(TokenBlacklistSerializer):

    def validate(self, attrs):
        
        refresh = attrs.get('refresh')

        if not refresh:
            raise_validation("Refresh token is required")

        refresh_token = RefreshToken(refresh)
        
        user_id = refresh_token.get('user_id')

        user = User.objects.get(id=user_id)

        if user is None:
            raise_validation("No user found")

        user.is_online = False
        user.last_login = timezone.now()

        user.save()

        return super().validate(attrs)
            

class CustomTokenVerifySerializer(TokenVerifySerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except Exception:
            raise AuthenticationFailed("Your session has expired. Please log in again.")

        return data


class ChangePasswordSerialzier(serializers.Serializer):

    current_password = DynamicCharField(min_length=8, write_only=True)
    new_password = DynamicCharField(min_length=8, write_only=True)
    confirm_password = DynamicCharField(min_length=8, write_only=True)


    def validate(self, attrs):
        
        current_password = attrs["current_password"]
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        request = self.context["request"]
        
        if not request.user.check_password(current_password):
            raise_validation(key="current_password", message="The current password you entered is incorrect.")
        
        if current_password == new_password:
            raise_validation(key="new_password", message="The new password cannot be the same as the old one.")

        if new_password != confirm_password:
            raise_validation(key="confirm_password" ,message="New and confirm password does not match")

        return attrs
    
    def update(self, instance, validated_data):

        instance.set_password(validated_data["new_password"])
        instance.save()

        # Keep session alive
        request = self.context.get("request")
        update_session_auth_hash(request, instance)
        # Return the new updated password
        return instance


class UpdateProfileSerializer(serializers.ModelSerializer):

    picture = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = Profile
        fields = ['picture']


    def to_representation(self, instance):

        data = super().to_representation(instance)

        data["profile"] = data.pop('picture')

        return data

    def update(self, instance, validated_data):

        if 'picture' in validated_data:
            instance.picture = validated_data.get('picture', None)

        instance.save(update_fields=['picture'])

        return instance

from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer, TokenBlacklistSerializer
from rest_framework import serializers
from django.db import transaction, IntegrityError
from apps.core.utils.validators import is_field_empty
from apps.core.utils.helpers import raise_validation
from django.contrib.auth import login, authenticate
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, Profile
from apps.core.utils.dynamic_char_field import DynamicCharField
from rest_framework.exceptions import AuthenticationFailed

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

        username = attrs.get('username')
        password = attrs.get('password')

        if is_field_empty(username):
            raise_validation("Username is required")

        if is_field_empty(password):
            raise_validation("Password is required")

        user = authenticate(request=request, username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        login(request, user)

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
            "username": user.username,
            "profile": picture_url,
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

    profile_image = serializers.ImageField(allow_null=True, required=False)

    username = DynamicCharField()

    password = DynamicCharField(min_length=8, write_only=True)

    confirm_password = DynamicCharField(min_length=8, write_only=True)

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise_validation("Passwords do not match.")

        return attrs
    

    def create(self, validated_data):
        
        try:

            with transaction.atomic():
                
                # Extract confirm password and profile image
                validated_data.pop('confirm_password')
                profile_image = validated_data.pop('profile_image', None)

                # User creation
                user = User.objects.create_user(
                    username=validated_data.get('username'),
                    password=validated_data.get('password')
                )

                # Profile creation
                Profile.objects.create(
                    user=user,
                    picture=profile_image
                )

                return user
        except IntegrityError:
            raise_validation("This username is already taken")
        except Exception:
            raise_validation("An error occurred during account creation.")

        
        
class LogoutBlacklistSerializer(TokenBlacklistSerializer):

    def validate(self, attrs):
        
        refresh = attrs.get('refresh')

        if not refresh:
            raise_validation("Refresh token is required")

        return super().validate(attrs)



    


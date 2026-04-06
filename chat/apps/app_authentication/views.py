from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenBlacklistView, TokenVerifyView
from rest_framework.throttling import ScopedRateThrottle
from apps.core.utils.response_message import response_message
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from .models import Profile
from django.core.management import call_command
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    CustomLoginObtainPairSerializer,
    CustomTokenRefreshSerializer,
    LogoutBlacklistSerializer,
    CustomTokenVerifySerializer,
    RegisterSerializer,
    ChangePasswordSerialzier,
    UpdateProfileSerializer
)

class CustomLoginObtainPairView(TokenObtainPairView):

    serializer_class = CustomLoginObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_limit'

    def post(self, request, *args, **kwargs):
        
        self.check_throttles(request)

        serializer = self.get_serializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        return response_message(
            message="Successfully logged in",
            data=serializer.validated_data
        )
    
class CustomTokenRefreshView(TokenRefreshView):

    serializer_class = CustomTokenRefreshSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_limit'

    def post(self, request, *args, **kwargs):
        
        self.check_throttles(request)

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return response_message(
            message="Successfully Refresh a token",
            data=serializer.validated_data
        )
    
class RegisterView(generics.CreateAPIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_limit'
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        
        self.check_throttles(request)

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return response_message(
            message="Successfully created an account",
            status_code=status.HTTP_201_CREATED
        )

class LogoutView(TokenBlacklistView):
    
    serializer_class = LogoutBlacklistSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return response_message(
            message="Successfully logged out",
            status_code=status.HTTP_205_RESET_CONTENT
        )


class CustomTokenVerifyView(TokenVerifyView):

    serializer_class = CustomTokenVerifySerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return response_message(
            message="Token is valid",
            status_code=status.HTTP_200_OK
        )


class ChangePasswordView(generics.UpdateAPIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_limit'
    serializer_class = ChangePasswordSerialzier
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):

        self.check_throttles(request)

        serializer = self.get_serializer(
            instance = request.user,
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return response_message(
            message="Successfully updated the password",
            status_code=status.HTTP_200_OK
        )

class UpdateProfileView(generics.UpdateAPIView):

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth_limit'
    serializer_class = UpdateProfileSerializer
    permission_classes = [IsAuthenticated]   
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request, *args, **kwargs):
        print(f"CONTENT_TYPE: {request.content_type}") # This should say multipart/form-data
        print(f"FILES: {request.FILES}") # Your image should be here
        self.check_throttles(request)

        profile, _ = Profile.objects.get_or_create(user=request.user)

        serializer = self.get_serializer(
            instance=profile,
            data=request.data,
            context={"request": request},
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return response_message(
            message="Successfully updated the profile picture",
            status_code=status.HTTP_200_OK,
            data=serializer.data
        )
        

def cleanup_expired_tokens():
    call_command('flushexpiredtokens')
    # python manage.py flushexpiredtokens
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenBlacklistView
from rest_framework.throttling import ScopedRateThrottle
from apps.core.utils.response_message import response_message
from rest_framework import status, generics
from django.core.management import call_command

from .serializers import (
    CustomLoginObtainPairSerializer,
    CustomTokenRefreshSerializer,
    LogoutBlacklistSerializer,
    RegisterSerializer
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

def cleanup_expired_tokens():
    call_command('flushexpiredtokens')
    # python manage.py flushexpiredtokens
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from apps.core.utils.response_message import response_message
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.management import call_command

from .serializers import (
    CustomLoginObtainPairSerializer,
    CustomTokenRefreshSerializer,
    RegisterSerializer
)

class CustomLoginObtainPairView(TokenObtainPairView):

    serializer_class = CustomLoginObtainPairSerializer
    throttle_classes = (ScopedRateThrottle, )

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)

        return response_message(
            success=True,
            message="Successfully logged in",
            data=serializer.data
        )
    
class CustomTokenRefreshView(TokenRefreshView):

    serializer_class = CustomTokenRefreshSerializer
    permission_classes = (IsAuthenticated,)
    throttle_classes = (ScopedRateThrottle, )

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return response_message(
            success=True,
            message="Successfully Refresh a token",
            data=serializer.data
        )
    

class RegisterView(generics.CreateAPIView):

    throttle_classes = (ScopedRateThrottle,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return response_message(
            success=True,
            message="Successfully created an account",
            status_code=status.HTTP_201_CREATED
        )

class LogoutView(APIView):

    permission_classes = (IsAuthenticated)

    def post(self, request):

        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()

        return response_message(
            success=True,
            message="Successfully logged out",
            status_code=status.HTTP_205_RESET_CONTENT
        )
    

def cleanup_expired_tokens():
    call_command('flushexpiredtokens')
    # python manage.py flushexpiredtokens
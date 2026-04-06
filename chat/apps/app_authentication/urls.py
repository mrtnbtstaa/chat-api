from django.urls import path

from .views import (
    LogoutView,
    CustomLoginObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    RegisterView,
    ChangePasswordView,
    UpdateProfileView
)

urlpatterns =[
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginObtainPairView.as_view(), name='login-obtain-pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('verify-token/', CustomTokenVerifyView.as_view(), name='verify-token'),
    path('passwords/', ChangePasswordView.as_view(), name='update-password'),
    path('profile/', UpdateProfileView.as_view(), name='update-profile')
]



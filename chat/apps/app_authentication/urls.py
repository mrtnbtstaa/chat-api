from django.urls import path
from .views import (
    LogoutView,
    CustomLoginObtainPairView,
    CustomTokenRefreshView,
    RegisterView
)

urlpatterns =[
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token-refresh')
]
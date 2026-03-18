from django.urls import path
from .views import (
    LogoutView,
    CustomLoginObtainPairView,
    CustomTokenRefreshView
)

urlpatterns =[
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', CustomLoginObtainPairView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token-refresh')
]
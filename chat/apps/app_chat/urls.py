from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ChatViewSet,
    ChatMessageViewSet
)

router = DefaultRouter()

router.register(r"messages", ChatMessageViewSet, basename='messages')
router.register(r"", ChatViewSet, basename='chats'),


urlpatterns = [
    path('', include(router.urls))
]
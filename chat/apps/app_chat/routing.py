from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Route for 1-to-1 Direct Messaging
    # Example ws/chat/direct/uuid/ -> uuid=8934-abc-123
    re_path(r"ws/chat/direct/(?P<receiver_id>[a-f0-9\-]{36})/$", consumers.DirectChatConsumer.as_asgi()),

    # Route for Group Chat
    # Example ws/chat/group/brodie/ -> brodie is the group_name
    re_path(r"ws/chat/group/(?P<group_name>[a-f0-9\-]{36})/$", consumers.GroupChatConsumer.as_asgi())
]
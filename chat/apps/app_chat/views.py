from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.decorators import action
from apps.core.pagination.pagination import CustomCursorPagination
from apps.core.serializers.base_feature_view_set import BaseFeatureViewSet
from .models import ChatRoom, Message
from apps.core.utils.response_message import response_message
from .serializers import (
    ListChatInboxUserSerializer,
    CreateMessageSerializer
)

class ChatViewSet(BaseFeatureViewSet):

    model = ChatRoom

    pagination_class = CustomCursorPagination

    queryset = ChatRoom.objects.all()

    serializer_action_classes = {
        "list": ListChatInboxUserSerializer,
        "send_direct_message": CreateMessageSerializer
    }
    prefetch_related_model = ['participants', 'messages', 'participants__user_profile']
    item_to_search = ['name', 'participants__username']

    def base_get_queryset(self):
        return ChatRoom.objects.all()
        
    @action(detail=False, methods=['post'], url_path='messages')
    def send_direct_message(self, request):

        recipient_id = request.data.get('recipient_id')

        room = ChatRoom.objects.filter(
            participants=request.user
        ).filter(
            participants__id=recipient_id
        ).first()

        if not room:
            # Create room and add the sender and recipient
            room = ChatRoom.objects.create(room_type=ChatRoom.RoomType.DIRECT)
            room.participants.add(request.user, recipient_id)


        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(sender=request.user, room=room)
        # Broadcast to WS
        self._broadcast_to_ws(recipient_id, serializer.data)

        return response_message(
            message=self.success_create_message,
            data=serializer.data
        )
    
    def _broadcast_to_ws(self, recipient_id, data):
        print("Broadcasting to the WS")
        channel_layer = get_channel_layer()

        ids = sorted([str(self.request.user.id), str(recipient_id)])
        room_group_name = f"chat_direct_{ids[0]}_{ids[1]}"

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "chat_message",
                "message": data
            }
        )






from asgiref.sync import async_to_sync
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from rest_framework.decorators import action
from apps.core.pagination.pagination import CustomCursorPagination
from apps.core.serializers.base_feature_view_set import BaseFeatureViewSet
from .models import ChatRoom, Message, ChatRoomReadState
from apps.core.utils.response_message import response_message
from django.db.models import OuterRef, Count, Q, Subquery
from django.db.models import Prefetch
from django.utils import timezone as tz
from datetime import timezone, datetime
from django.db.models.functions import Coalesce
from django.db.models import Value, BooleanField, Q
from django.db.models.functions import Lower
from .serializers import (
    ListChatInboxUserSerializer,
    CreateMessageSerializer,
    MessageChatListSerializer
)

class ChatViewSet(BaseFeatureViewSet):

    model = ChatRoom
    pagination_class = CustomCursorPagination

    serializer_action_classes = {
        "list": ListChatInboxUserSerializer,
    }

    item_to_search = [
        'participants__full_name'
    ]
        
    def base_get_queryset(self):

        current_user = self.request.user

        if not current_user.is_authenticated:
            return ChatRoom.objects.none()
        
        last_read_subquery = ChatRoomReadState.objects.filter(
            user=current_user, 
            room=OuterRef('pk')
        ).values('last_read_at')[:1]

        fallback_date = datetime(1900, 1, 1, tzinfo=timezone.utc)

        return ChatRoom.objects.filter(
            participants=current_user
        ).annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__created_at__gt=Coalesce(
                    Subquery(last_read_subquery),
                    fallback_date
                )) &
                ~Q(messages__sender=current_user)
            )
        ).distinct()

    def get_queryset(self):

        current_user = self.request.user

        qs = self.base_get_queryset()

        latest_messages_qs = Message.objects.filter(
            room__participants=current_user,
        ).order_by('-created_at')

        qs = qs.prefetch_related(
            'participants',
            'participants__user_profile',
            'read_states',
            Prefetch('messages', queryset=latest_messages_qs, to_attr='latest_msgs')
        )

        qs = self.apply_search(qs)

        return qs.distinct().order_by(*self.ordering_fields)

        
    @action(detail=True, methods=['PATCH'], serializer_class=None)
    def mark_as_read(self, request, id=None):

        room = self.get_object()

        # Get the latest message id
        last_message = room.messages.order_by('-created_at').first()
        last_msg_id = last_message.id if last_message else None

        ChatRoomReadState.objects.update_or_create(
            user=request.user,
            room=room,
            defaults={
                'last_read_at': tz.now(),
                'last_read_message_id': last_msg_id
            }
        )
        return response_message(message="Marked as read", data={'last_read_at': tz.now()})
    

class ChatMessageViewSet(BaseFeatureViewSet):

    model = Message
    pagination_class = CustomCursorPagination
    permission_classes = [IsAuthenticated]

    serializer_action_classes = {
        # "send_message": CreateMessageSerializer,
        "list": MessageChatListSerializer
    }

    item_to_search = ['text']

    select_related_model = ['sender__user_profile', 'sender']
    @action(detail=False, methods=['post'], url_path='messages')
    def send_message(self, request):
        return self.send_message(request)

    def base_get_queryset(self):
        return Message.objects.filter(
            room__participants=self.request.user
        ).select_related(
            'sender', 
            'sender__user_profile'
        ).annotate(
            # Handle the lowercase name in the DB
            lowered_sender_name=Lower('sender__full_name'),
            # Handle the "sent_by_me" logic in the DB
            is_sent_by_me=Q(sender_id=self.request.user.id)
        ).only(
            'id',
            'text',
            'created_at',
            'sender__id',
            'sender__full_name',
            'sender__is_online',
            'sender__user_profile__picture'
        ).order_by('-created_at')
    
    def send_message(self, request):

        current_user = request.user

        recipient_id = request.data.get('recipient_id')

        room = ChatRoom.objects.filter(
            participants=current_user,
            room_type=ChatRoom.RoomType.DIRECT
        ).filter(
            participants__id=recipient_id
        ).first()


        if not room:
            # Create room and add the sender and recipient
            room = ChatRoom.objects.create(room_type=ChatRoom.RoomType.DIRECT)
            room.participants.add(current_user, recipient_id)


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=current_user, room=room)

        # Update so the message that just got sent isn't unread
        ChatRoomReadState.objects.update_or_create(
            user=current_user,
            room=room,
            defaults={'last_read_at': tz.now()}
        )

        # Broadcast to WS
        self._broadcast_to_ws(recipient_id, serializer.data)
        self._broadcast_to_inbox(recipient_id, {
            "last_message": request.data.get('text'),
            "chat_id": str(room.id),
        })

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

    def _broadcast_to_inbox(self, inbox_name, data):
        channel_layer = get_channel_layer()

        room_inbox_name = f"chat_inbox_{inbox_name}";
    
        async_to_sync(channel_layer.group_send)(
            room_inbox_name,
            {
                "type": "inbox_message",
                "message": data
            }
        )
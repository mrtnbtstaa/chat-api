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
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower
from .serializers.chat_inbox_serializer import(
    ListChatInboxUserSerializer,
    ListChatUsersSerializer
)
from .serializers.chat_message_serializer import (
    MessageChatListSerializer,
    SendMessageSerializer
)
from .serializers.group_chat_serializer import (
    CreateGroupChatSerializer,
    ParticipantSerializer,
)


User = get_user_model()


class ChatViewSet(BaseFeatureViewSet):

    model = ChatRoom
    pagination_class = CustomCursorPagination

    serializer_action_classes = {
        "list": ListChatInboxUserSerializer,
        'get_chat_users': ListChatUsersSerializer
    }

    item_to_search = ['participants__full_name']
        
    def base_get_queryset(self):

        current_user = self.request.user
        
        last_read_subquery = ChatRoomReadState.objects.filter(
            user=current_user, 
            room=OuterRef('pk')
        ).values('last_read_at')[:1]

        fallback_date = datetime(1900, 1, 1, tzinfo=timezone.utc)

        return ChatRoom.objects.filter(
            participants=current_user
        ).annotate(
            total_messages=Count('messages'),
            unread_count=Count(
                'messages',
                filter=Q(messages__created_at__gt=Coalesce(
                    Subquery(last_read_subquery),
                    fallback_date
                )) &
                ~Q(messages__sender=current_user)
            )
        ).exclude(total_messages=0).distinct() # Exclude rooms that has zero messages total

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

    
    @action(detail=False, methods=['GET'], url_path='users')
    def get_chat_users(self, request):
        
        chats = ChatRoom.objects.filter(
            participants=request.user,
        ).prefetch_related('participants')

        page = self.paginate_queryset(chats)

        if page:

            serializer = self.get_serializer(page, many=True)

            paginated_data = self.get_paginated_response(serializer.data)

        return response_message(
            message="List chat users",
            data=paginated_data.data
        )

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
        "create": SendMessageSerializer,
        "list": MessageChatListSerializer
    }

    item_to_search = ['text']

    select_related_model = ('sender__user_profile', 'sender')

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
    

    def perform_create(self, serializer):
        # Save the message object
        instance = serializer.save()

        # Re-fetch the instance using the base_get_queryset
        message = self.base_get_queryset().filter(pk=instance.pk).first()

        # Gets the serialized data for the broadcast
        message_data = MessageChatListSerializer(
            message,
            context={'request': self.request}
        ).data

        recipient_id = self.request.data.get('recipient_id')
        # Push the message to the specific WS Group
        self._send_broadcasts(recipient_id, message_data)

        return message_data 

    
    def _send_broadcasts(self, recipient_id, data):

        channel_layer = get_channel_layer()
        
        # Direct Chat Broadcast
        # Sorting IDs ensures both users are in the same group name
        user_ids = sorted([str(self.request.user.id), str(recipient_id)])
        room_group_name = f"chat_direct_{user_ids[0]}_{user_ids[1]}"
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "chat_message",
                "message": data
            }
        )
        # Inbox/Activity Broadcast
        # Notify the recipient's specific inbox group
        recipient_inbox = f"chat_inbox_{recipient_id}"
        async_to_sync(channel_layer.group_send)(
            recipient_inbox,
            {
                "type": "inbox_message",
                "message": data
            }
        )

class ChatGroupViewSet(BaseFeatureViewSet):

    pagination_class = CustomCursorPagination
    model = User
    permission_classes = [IsAuthenticated]

    serializer_action_classes = {
        "create": CreateGroupChatSerializer,
        "list": ParticipantSerializer

    }

    def base_get_queryset(self):
        return (
            User.objects.filter(rooms__participants=self.request.user)
            .only(
                'id', 'full_name', 'is_online', 'user_profile__picture', 'user_profile__id'
            )
            .exclude(id=self.request.user.id)
            .select_related('user_profile')
            .distinct()
        )
            
        





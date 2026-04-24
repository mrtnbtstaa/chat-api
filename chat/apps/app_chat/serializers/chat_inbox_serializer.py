from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import ChatRoom, Message, ChatRoomReadState
from django.utils import timezone as tz
from django.db import transaction
from apps.core.utils.helpers import raise_validation
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.core.utils.serializer_fields import DynamicCharField, Base64ImageField, DynamicUUIDField

class ListChatInboxUserSerializer(serializers.ModelSerializer):

    chat_id = serializers.UUIDField(source='id')
    last_message = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'chat_id',
            'room_type',
            'created_at',
            'unread_count',
            'recipient',
            'last_message',
        ]

    def get_recipient(self, obj):

        if obj.room_type == ChatRoom.RoomType.GROUP:
            return None
        
        request = self.context["request"]

        current_user = request.user if request else None

        # Find the participants who is not the current user
        # User first() to get the single user on the other end
        other_participant = obj.participants.exclude(id=current_user.id).first()

        # Fallback if chat with yourself or no other user exists
        if not other_participant:
            other_participant = current_user

        return {
            "user_id": other_participant.id,
            "display_full_name": other_participant.full_name,
            "is_online": getattr(other_participant, 'is_online', False),
            "profile_image": self.get_profile_image(other_participant, request)
        }
    
    def get_profile_image(self, user, request):
        try:
            if hasattr(user, 'user_profile') and user.user_profile.picture:
                return request.build_absolute_uri(user.user_profile.picture.url)
        except:
            pass
        return None

    def get_last_message(self, obj):

        messages = getattr(obj, 'latest_msgs', [])

        if not messages:
            return None

        last_message = messages[0]
        
        return {
            "message_id": last_message.id,
            "text": last_message.text[:15],
            "sender": last_message.sender.full_name,
            "last_message_at": last_message.created_at
        }  
    

class ListChatUsersSerializer(serializers.ModelSerializer):

    chat_id = serializers.UUIDField(source='id')
    recipient = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'chat_id',
            'room_type',
            'created_at',
            'recipient',
        ]

    def get_recipient(self, obj):

        if obj.room_type == ChatRoom.RoomType.GROUP:
            return None
        
        request = self.context["request"]

        current_user = request.user if request else None

        # Find the participants who is not the current user
        # User first() to get the single user on the other end
        other_participant = obj.participants.exclude(id=current_user.id).first()

        # Fallback if chat with yourself or no other user exists
        if not other_participant:
            other_participant = current_user

        return {
            "user_id": other_participant.id,
            "display_full_name": other_participant.full_name,
            "is_online": getattr(other_participant, 'is_online', False),
            "profile_image": self.get_profile_image(other_participant, request)
        }
    
    def get_profile_image(self, user, request):
        try:
            if hasattr(user, 'user_profile') and user.user_profile.picture:
                return request.build_absolute_uri(user.user_profile.picture.url)
        except:
            pass
        return None
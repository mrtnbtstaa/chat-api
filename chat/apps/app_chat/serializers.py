from rest_framework import serializers
from rest_framework import status
from apps.core.utils.helpers import raise_validation
from channels.layers import channel_layers
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class CreateGroupChatSerializer(serializers.ModelSerializer):
    pass

class CreateMessageSerializer(serializers.ModelSerializer):
    pass

class ListChatUserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    display_image = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'room_type',
            'display_name',
            'display_image',
            'last_message',
            'created_at'
        ]

    def display_name(self, obj):

        if obj.room_type == ChatRoom.RoomType.GROUP:
            return None

        user = self.context["request"].user

        # Return the other person's username
        other_participants = obj.participants.exclude(id=user.id).first()

        return other_participants.username if other_participants else "Unknown user"
    
    def get_display_image(self, obj):

        # If it's a group, can display the group icon
        if obj.room_type == ChatRoom.RoomType.GROUP:
            return None #
        
        # Return the other person's profile picture
        user = self.context["user"].user

        other_participant = obj.participants.exclude(id=user.id).first()

        if other_participant and hasattr(other_participant, 'user_profile'):
            return other_participant.user_profile.picture.url
        return None

    def get_last_message(self, obj):

        last_message = obj.messages.order_by('-created_at').latest()
        if last_message:
            return {
                "text": last_message.text[:15],
                "sender": last_message.sender.username,
                "timestamp": last_message.created_at
            }  

from rest_framework import serializers
from rest_framework import status
from apps.core.utils.helpers import raise_validation
from channels.layers import channel_layers
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class GroupChatSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'slug', 'room_type']
        read_only_fields = ['id', 'slug', 'room_type']

    def create(self, validated_data):
        # Set the room_type as GROUP
        validated_data['room_type'] = ChatRoom.RoomType.GROUP
        user = self.context['request'].user

        # Create the room (Slug is handled in model.save())
        room = ChatRoom.objects.create(**validated_data)

        # Add the creator as participants
        room.participants.add(user)

        return room
    

class CreateMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["sender_id"] = str(instance.sender.id)

        data.pop('id')
        return data


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

    def get_display_name(self, obj):

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
        request = self.context["request"]

        user = request.user

        other_participant = obj.participants.exclude(id=user.id).first()

        if other_participant and hasattr(other_participant, 'user_profile'):
            return request.build_absolute_uri(other_participant.user_profile.picture.url)
        return None

    def get_last_message(self, obj):

        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                "text": last_message.text[:15],
                "sender": last_message.sender.username,
                "last_message_at": last_message.created_at
            }  

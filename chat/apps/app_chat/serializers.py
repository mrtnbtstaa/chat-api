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

        data.update({
            "sender_id": str(instance.sender.id),
            "is_online": getattr(getattr(instance, 'sender'), 'is_online', False)
        })

        data.pop('id')
        return data


class ListChatInboxUserSerializer(serializers.ModelSerializer):

    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'room_type',
            'last_message',
            'created_at'
        ]

    def to_representation(self, instance):

        data = super().to_representation(instance)

        if data["room_type"] == ChatRoom.RoomType.GROUP:
            return None
        
        request = self.context["request"]

        current_user = request.user if request else None

        # Find the participants who is not the current user
        # User first() to get the single user on the other end
        other_participant = instance.participants.exclude(id=current_user.id).first()

        # Fallback if chat with yourself or no other user exists
        if not other_participant:
            other_participant = current_user

        if other_participant:
            data.update({
                "username": other_participant.username,
                "first_name": other_participant.first_name,
                "last_name": other_participant.last_name,
                "is_online": getattr(other_participant, 'is_online', False),
                "profile_image": self.get_profile_image(other_participant, request)
            })

        return data
    

    def get_profile_image(self, user, request):
        try:
            if hasattr(user, 'user_profile') and user.user_profile.picture:
                return request.build_absolute_uri(user.user_profile.picture.url)
        except:
            pass
        return None

 
    def get_last_message(self, obj):

        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                "text": last_message.text[:15],
                "sender": last_message.sender.username,
                "last_message_at": last_message.created_at
            }  

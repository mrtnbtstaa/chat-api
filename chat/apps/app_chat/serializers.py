from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from datetime import datetime

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

        picture = None

        request = self.context["request"]

        data = super().to_representation(instance)

        user_profile = getattr(instance.sender, 'user_profile', None)

        if user_profile and user_profile.picture:
            picture = request.build_absolute_uri(getattr(user_profile, 'picture', None).url)

        data.update({
            "id": str(instance.id),
            "recipient": {
                "profile_image": picture,  
                "is_online": getattr(getattr(instance, 'sender'), 'is_online', False),
                "sender": instance.sender.full_name,
                "sender_id": str(instance.sender.id),
                "sent_by_me": instance.sender.id == request.user.id
            }
        })

        return data


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
            # "username": other_participant.username,
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
    

class ListChatMessagesSerializer(serializers.ModelSerializer):

    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['room_type', 'messages']


    def get_messages(self, obj):

        messages = getattr(obj, 'latest_msgs', [])


        for message in messages:
            print(message)

        return obj



    
class MessageChatListSerializer(serializers.ModelSerializer):


    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at']


    def to_representation(self, instance):

        data = super().to_representation(instance)

        data["recipient"] = {
            "profile_image": self.context['request'].build_absolute_uri(instance.sender.user_profile.picture.url) if instance.sender.user_profile.picture else None,
            "is_online": instance.sender.is_online,
            "sender_id": str(instance.sender.id),
            "sender": instance.lowered_sender_name,
            "sent_by_me": instance.is_sent_by_me
        }

        return data
    


    

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import ChatRoom, Message, ChatRoomReadState
from django.utils import timezone as tz
from django.db import transaction
from apps.core.utils.helpers import raise_validation
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.core.utils.serializer_fields import DynamicCharField, Base64ImageField, DynamicUUIDField

User = get_user_model()

class SendMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['text', 'created_at']
    
    def create(self, validated_data):
    
        with transaction.atomic():

            request = self.context["request"]
            recipient_id = request.data.get('recipient_id')
            current_user = request.user

            # Find or create room if not found
            room = ChatRoom.objects.filter(
                participants=current_user,
                room_type=ChatRoom.RoomType.DIRECT
            ).filter(
                participants__id=recipient_id
            ).first()

            if not room:
                room = ChatRoom.objects.create(room_type=ChatRoom.RoomType.DIRECT)
                room.participants.add(current_user, recipient_id)

            # Create the message
            message = Message.objects.create(
                sender=current_user,
                room=room,
                text=validated_data.get('text')
            )

            # Update the read state
            ChatRoomReadState.objects.update_or_create(
                user=current_user,
                room=room,
                defaults={'last_read_at': tz.now()}
            )

            return message



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
        
class MessageChatListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at']

    def to_representation(self, instance):

        data = super().to_representation(instance)

        user_profile = getattr(instance.sender, 'user_profile', None)

        data["recipient"] = {
            "profile_image": self.context['request'].build_absolute_uri(user_profile.picture.url) if user_profile.picture else None,
            "is_online": instance.sender.is_online,
            "sender_id": str(instance.sender.id),
            "sender": instance.lowered_sender_name,
            "sent_by_me": instance.is_sent_by_me
        }

        return data
    


    

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import ChatRoom
from apps.core.utils.helpers import raise_validation
from apps.core.utils.serializer_fields import DynamicCharField, Base64ImageField, DynamicUUIDField

User = get_user_model()

class CreateGroupChatSerializer(serializers.Serializer):
    
    name = DynamicCharField()
    participants = serializers.ListField(
        child=DynamicUUIDField(),
        write_only=True
    )
    chat_group_image = Base64ImageField(required=False)

    def validate(self, attrs):
        participant_ids = attrs.get('participants', [])

        # Fetch only the IDs that actually exist user database
        valid_ids = list(
            User.objects.filter(id__in=participant_ids)
            .values_list('id', flat=True)
        )

        # Check if the resulting list is empty
        if not valid_ids:
            raise_validation("At least one valid participant is required.")

        # Replace the input list with the sanitized list
        attrs['participants'] = valid_ids
            
        return attrs

    def create(self, validated_data):

        current_user = self.context['request'].user

        participants = validated_data.pop('participants', [])

        # Create the room (Slug is handled in model.save())
        room = ChatRoom.objects.create(**validated_data, room_type=ChatRoom.RoomType.GROUP)

        # Add the creator as participants
        room.participants.add(current_user, *participants)

        return room
    


class ParticipantSerializer(serializers.ModelSerializer):
    user_id = DynamicUUIDField(source='id')
    profile_image = serializers.ImageField(source='user_profile.picture', read_only=True)
    
    class Meta:
        model = User 
        fields = ['user_id', 'full_name', 'is_online', 'profile_image']




    
 

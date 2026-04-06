from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models.models import UUIDTimestampModel
from django.utils.text import slugify

User = get_user_model()

class ChatRoom(UUIDTimestampModel):
    
    class RoomType(models.TextChoices):
        DIRECT = 'DIRECT', 'Direct'
        GROUP = 'GROUP', 'Group'

    room_type = models.CharField(
        max_length=7,
        choices=RoomType.choices,
        default=RoomType.DIRECT
    )

    name = models.CharField(max_length=30, blank=True, null=True) # Name of the group chat
    slug = models.CharField(max_length=30, blank=True, null=True) # Slug of the url of the group chat
    participants = models.ManyToManyField(User, related_name='rooms') # Participants of the group chat

    def __str__(self):
        return self.name if self.name else f"Direct-{self.id}"
    
    def save(self, *args, **kwargs):
        if self.room_type == self.RoomType.GROUP and self.name and not self.slug:
            self.slug = slugify(self.name) 
        return super().save(*args, **kwargs)
    
    def get_group_name(self, recipient_id):
        if self.room_type == self.RoomType.GROUP:
            return f"chat_group_{self.slug}"
        return f"chat_direct_{str(recipient_id)}"
    
    class Meta:
        indexes = [
            models.Index(fields=['name']), # Fast lookup for group search by name
            models.Index(fields=['slug']) # Fast lookup for URLs and room
        ]
    
class Message(UUIDTimestampModel):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    
    class Meta:
        indexes = [models.Index(fields=['room', '-created_at'])]
        ordering = ['-created_at'] 


class ChatRoomReadState(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_read_states')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='read_states')

    last_read_message_id = models.UUIDField(null=True, blank=True)

    # Timestamp used to calculate unread count messages
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'room')
        

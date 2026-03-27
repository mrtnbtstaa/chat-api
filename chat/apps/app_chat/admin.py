from django.contrib import admin
from .models import ChatRoom, Message, ChatRoomReadState
# Register your models here.

@admin.register(ChatRoom)
class AdminChatRoom(admin.ModelAdmin):
    pass

@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    pass

@admin.register(ChatRoomReadState)
class AdminChatRoomReadState(admin.ModelAdmin):
    readonly_fields = ('last_read_at', )

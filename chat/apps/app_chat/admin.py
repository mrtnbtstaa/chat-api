from django.contrib import admin
from .models import ChatRoom, Message
# Register your models here.

@admin.register(ChatRoom)
class AdminChatRoom(admin.ModelAdmin):
    pass

@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    pass

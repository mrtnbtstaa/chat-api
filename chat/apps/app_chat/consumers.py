import json

from channels.generic.websocket import AsyncWebsocketConsumer

class BaseChatConsumer(AsyncWebsocketConsumer):


    async def connect(self):

        self.user = self.scope["user"]


        print(f"User: {self.user}")
        
        # If user is anonymous 
        if self.user.is_anonymous:
            await self.close(code=4003, reason="Anonymous user")
            return
                
        # Create room and join the room
        self.room_group_name = await self.get_room_name()      

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        print("Connected to WS")

        # Accept the connection
        await self.accept()

    async def disconnect(self, code):

        try:
            if hasattr(self, 'room_group_name') and self.room_group_name:
                # Leave room group
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )
        except Exception as e:
            print(e)

    async def receive(self, text_data = None, bytes_data = None):
        
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON data."}))
            return
        
        # Check if the packet is typing indicator
        if data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_status", 
                    "user_id": str(self.user.id),
                    "username": self.user.username,
                    "is_typing": data.get("is_typing", False)
                }
            )
            
    async def get_room_name(self):
        raise NotImplementedError("Subclasses must implement get_room_name")
    
    # Chat message handler
    async def chat_message(self, event):
        message_data = event["message"]
        message_data["sent_by_me"] = (message_data.get("sender_id") == str(self.user.id))
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "data": message_data
        }))

    # Typing status handler
    async def typing_status(self, event):
        # Dont send the typing indicator back to the user who is typing
        if event["user_id"] != str(self.user.id):
            await self.send(
                text_data=json.dumps({
                    "type": "typing",
                    "username": event["username"],
                    "is_typing": event["is_typing"],
                    "user_id": event["user_id"]
                })
            )


    async def inbox_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
    

# Direct Chat Consumer
class DirectChatConsumer(BaseChatConsumer):
    async def get_room_name(self):
        receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]
        ids = sorted([str(self.scope["user"].id), str(receiver_id)])
        print(f"Direct consumer: ${ids[0]} --------- ${ids[1]}")
        return f"chat_direct_{ids[0]}_{ids[1]}"
    

# Group Chat Consumer
class GroupChatConsumer(BaseChatConsumer):
    async def get_room_name(self):
        group_name = self.scope["url_route"]["kwargs"]["group_name"]
        return f"chat_group_{group_name}"


# Chat Inbox Consumer
class ChatInboxConsumer(BaseChatConsumer):
    async def get_room_name(self):
        inbox_name = self.scope["url_route"]["kwargs"]["inbox_name"]
        return f"chat_inbox_{inbox_name}"

    
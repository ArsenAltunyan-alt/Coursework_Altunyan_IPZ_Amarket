import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from asgiref.sync import sync_to_async
from .models import Message, Conversation
from announcement.models import Announcement

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user1 = self.scope['user'].username 
        user2 = self.room_name
        self.room_group_name = f"chat_{''.join(sorted([user1, user2]))}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        announcement_id = text_data_json.get('announcement_id')
        sender = self.scope['user']  
        receiver = await self.get_receiver_user() 
        
        message_id, announcement_payload = await self.save_message(sender, receiver, message, announcement_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            
            {
                'type': 'chat_message',
                'sender': sender.username,
                'receiver': receiver.username,
                'message': message,
                'message_id': message_id,
                'image_url': '',
                'announcement': announcement_payload,
            }
        )
        

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        message_id = event.get('message_id')
        image_url = event.get('image_url', '')
        announcement_payload = event.get('announcement')

        await self.send(text_data=json.dumps({
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'message_id': message_id,
            'image_url': image_url,
            'announcement': announcement_payload,
        }))

        if message_id and self.scope['user'].username == receiver:
            await self.mark_message_read(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'reader': receiver,
                }
            )

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'reader': event['reader'],
        }))

    @sync_to_async
    def save_message(self, sender, receiver, message, announcement_id):
        Conversation.get_or_create_between(sender, receiver)
        announcement = None
        if announcement_id:
            try:
                announcement = Announcement.objects.get(pk=announcement_id)
            except Announcement.DoesNotExist:
                announcement = None
        new_message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message,
            announcement=announcement,
        )
        announcement_payload = None
        if announcement:
            announcement_payload = {
                'id': announcement.id,
                'title': announcement.title,
                'url': reverse('announcement:detail', args=[announcement.id]),
                'seller_username': announcement.seller.username,
            }
        return new_message.id, announcement_payload

    @sync_to_async
    def get_receiver_user(self):
        return User.objects.get(username=self.room_name)

    @sync_to_async
    def mark_message_read(self, message_id):
        Message.objects.filter(id=message_id, is_read=False).update(
            is_read=True,
            read_at=timezone.now(),
        )

from __future__ import absolute_import, unicode_literals

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .tasks import announce

SURVEY = (
    "Would you like to take a survey?",
    "Do you eat beans?",
    "Would you like to see a new movie starring George Wendt?",
    "Do you eat beans with George Wendt?",
    "Would you like to see George Wendt eating beans in a movie?",
    "Do you eat beans at George Wendt movies?",
    "Would you like to see George Wendt in a bean-eating movie?",
    "How many beans do you eat in a George Wendt bean-eating movie?",
    "How many bean-eating movies have you seen with George Wendt?",
    "If you were a bean what kind of bean would you be?",
    "Have a great day!",
)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        for i, question in enumerate(SURVEY):
            announce.apply_async((self.room_group_name, question), countdown=i * 8)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

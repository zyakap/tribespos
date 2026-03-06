import json
from channels.generic.websocket import AsyncWebsocketConsumer


class KitchenConsumer(AsyncWebsocketConsumer):
    KITCHEN_GROUP = 'kitchen_display'

    async def connect(self):
        await self.channel_layer.group_add(self.KITCHEN_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.KITCHEN_GROUP, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'ticket_update':
            await self.channel_layer.group_send(
                self.KITCHEN_GROUP,
                {'type': 'kitchen_ticket', 'data': data}
            )

    async def kitchen_ticket(self, event):
        await self.send(text_data=json.dumps(event['data']))

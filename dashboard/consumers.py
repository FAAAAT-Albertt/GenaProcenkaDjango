import asyncio
import json
import time
import random
from threading import Thread

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import DenyConnection

from .api import amry_api
from .api import armtek_api
from .api import carreta_api
from .api import emex_api

class DetailConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        """Функция подключения клиента к WebSocket"""
        await self.channel_layer.group_add(
            "group",
            self.channel_name
        )

        await self.accept()
        
        if self.scope['query_string'] == b'from=site':
            self.parse = True
            _thread = Thread(target=self.simulate)
            _thread.start()

    async def send_message(self, event):
        """Функция отправки сообщения на клиент"""
        await self.send(json.dumps(event['message']))

    async def disconnect(self, close_code):
        self.parse = False

    async def receive(self, text_data):
        # await self.send(text_data)
        await self.channel_layer.group_send(
            "group",
            {
                "type": "send_message",
                "message": json.loads(text_data),
            }
        )

    def simulate(self):
        pass
        # amry_thread = Thread(target=self.start_amry, args=('amry',))
        # amry_thread.start()
        # armtek_thread = Thread(target=self.start_amry, args=('armtek',))
        # armtek_thread.start()
        # carreta_thread = Thread(target=self.start_amry, args=('carreta',))
        # carreta_thread.start()
        # emex_thread = Thread(target=self.start_amry, args=('emex',))
        # emex_thread.start()
            

    def start_amry(self, site):
        if site == "amry":
            asyncio.run(amry_api.main())
        elif site == "armtek":
            asyncio.run(armtek_api.main())
        elif site == "carreta":
            asyncio.run(carreta_api.main())
        elif site == "emex":
            asyncio.run(emex_api.main())
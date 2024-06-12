import asyncio
import json
import time
import random
from threading import Thread
import pandas as pd

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import DenyConnection
from .models import DetailAmry, MyPrice

from .api import amry_api
from .api import armtek_api
from .api import carreta_api
from .api import emex_api

class DetailConsumer(AsyncJsonWebsocketConsumer):

    i = 0
    page = 1
    max_page = 0

    async def connect(self):
        """Функция подключения клиента к WebSocket"""
        await self.channel_layer.group_add(
            "group",
            self.channel_name
        )

        await self.accept()
        
        if self.scope['query_string'] == b'from=site':
            self.i = 0
            self.parse = True
            _thread = Thread(target=self.simulate)
            _thread.start()
            details = DetailAmry.objects.all()

    async def send_message(self, event):
        """Функция отправки сообщения на клиент"""
        await self.send(json.dumps(event['message']))

    async def disconnect(self, close_code):
        self.parse = False

    async def receive(self, text_data):
        data = json.loads(text_data)
        if "message" in data:
            if data["message"] == "next_page":
                self.i = 0
                self.page += 1
                if self.page <= self.max_page:
                    base_thread = Thread(target=self.database_price_page)
                    base_thread.start()
                else:
                    base_thread = Thread(target=self.database_prices)
                    base_thread.start()
                return
            elif data["message"] == "prev_page":
                self.i = 0
                self.page -= 1
                if self.page == 0:
                    self.page = 1
                base_thread = Thread(target=self.database_price_page)
                base_thread.start()
                return
        await self.channel_layer.group_send(
            "group",
            {
                "type": "send_message",
                "message": json.loads(text_data),
            }
        )

    def simulate(self):
        base_thread = Thread(target=self.database_prices)
        base_thread.start()
        # amry_thread = Thread(target=self.start_amry, args=('amry',))
        # amry_thread.start()
        # armtek_thread = Thread(target=self.start_amry, args=('armtek',))
        # armtek_thread.start()
        # carreta_thread = Thread(target=self.start_amry, args=('carreta',))
        # carreta_thread.start()
        # emex_thread = Thread(target=self.start_amry, args=('emex',))
        # emex_thread.start()
        percent = 0.5
        while True:
            prices = MyPrice.objects.filter(send=False)
            for price in prices:
                price.amry = random.randint(int(price.buyPrice - price.buyPrice * percent), int(price.buyPrice + price.buyPrice * percent))
                price.armtek = random.randint(int(price.buyPrice - price.buyPrice * percent), int(price.buyPrice + price.buyPrice * percent))
                price.carreta = random.randint(int(price.buyPrice - price.buyPrice * percent), int(price.buyPrice + price.buyPrice * percent))
                price.emex = random.randint(int(price.buyPrice - price.buyPrice * percent), int(price.buyPrice + price.buyPrice * percent))
                price.save()
                time.sleep(0.4)

            
    def start_amry(self, site):
        if site == "amry":
            self.get_price_amry()
        elif site == "armtek":
            asyncio.run(armtek_api.main())
        elif site == "carreta":
            asyncio.run(carreta_api.main())
        elif site == "emex":
            asyncio.run(emex_api.main())

    def get_price_amry(self):
        prices = MyPrice.objects.filter(send=False, amry=0)
        for row in prices:
            detail = DetailAmry.objects.filter(article = row.article).order_by('-price').first()
            if not detail is None:
                row.amry = detail.price
                row.save()

    def database_prices(self):
        while self.i < 5:
            prices = MyPrice.objects.filter(send=False).exclude(amry=0, armtek=0, carreta=0, emex=0)
            for price in prices:
                if self.i < 5:
                    row = {
                        'detail' : price.detail,
                        'article' : price.article,
                        'price' : price.buyPrice,
                        'carreta' : price.carreta,
                        'amry' : price.amry,
                        'armtek' : price.armtek,
                        'emex' : price.emex
                    }
                    asyncio.run(self.send(json.dumps(row)))
                    price.send = True
                    price.page = self.page
                    price.save()
                    self.i += 1
                else: 
                    continue
        self.max_page = self.page
        
    def database_price_page(self):
        prices = MyPrice.objects.filter(page=self.page)
        for price in prices:
            row = {
                'detail' : price.detail,
                'article' : price.article,
                'price' : price.buyPrice,
                'carreta' : price.carreta,
                'amry' : price.amry,
                'armtek' : price.armtek,
                'emex' : price.emex
            }
            asyncio.run(self.send(json.dumps(row)))
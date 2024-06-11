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
            details = DetailAmry.objects.all()

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
                time.sleep(0.1)

            
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
        column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
        df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
        json_data = df.to_dict(orient="records")
        for row in json_data:
            detail = DetailAmry.objects.filter(article = str(row['Article'])).order_by('-price').first()
            if not detail is None:
                result_my = {
                    'column' : 'amry',
                    'articul' : detail.article,
                    'price' : detail.price,
                }
                asyncio.run(self.send(json.dumps(result_my)))

    def database_prices(self):
        while True:
            prices = MyPrice.objects.filter(send=False).exclude(amry=0, armtek=0, carreta=0, emex=0)
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
                price.send = True
                price.save()
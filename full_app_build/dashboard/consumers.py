import asyncio
import json
import time
import random
from threading import Thread
import pandas as pd

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models.functions import Lower
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
        await MyPrice.objects.all().adelete()

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
        # base_thread = Thread(target=self.database_prices)
        # base_thread.start()
        amry_thread = Thread(target=self.start_amry, args=('amry',))
        amry_thread.start()
        armtek_thread = Thread(target=self.start_amry, args=('armtek',))
        armtek_thread.start()
        carreta_thread = Thread(target=self.start_amry, args=('carreta',))
        carreta_thread.start()
        emex_thread = Thread(target=self.start_amry, args=('emex',))
        emex_thread.start()

        amry_thread.join()
        armtek_thread.join()
        carreta_thread.join()
        emex_thread.join()

        self.send_rows()


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
        index = 0
        all_prices = len(MyPrice.objects.all())
        while index < all_prices:
            prices = MyPrice.objects.filter(send=False, amry=0)
            for row in prices:
                brand = row.brand.strip().lower()
                detail = DetailAmry.objects.filter(article = row.article, brand__iexact = brand, quantity__gt = 1).order_by('-price').first()
                if not detail is None:
                    MyPrice.objects.filter(article = row.pk).update(amry = detail.price)
                
                index += 1

    def database_prices(self):
        all_prices = MyPrice.objects.all()
        if (self.page != 1 and len(all_prices) >= (self.page - 1) * 50) or self.page == 1:
            while self.i < 50:
                prices = MyPrice.objects.filter(send=False)
                for price in prices:
                    if self.i < 50 and price.emex != 0 and price.carreta != 0 and price.armtek != 0:
                        row = {
                            'detail' : price.detail,
                            'article' : price.article,
                            'price' : price.buyPrice,
                            'carreta' : price.carreta,
                            'amry' : price.amry,
                            'armtek' : price.armtek,
                            'emex' : price.emex
                        }
                        time.sleep(0.1)
                        asyncio.run(self.send(json.dumps(row)))
                        price.send = True
                        price.page = self.page
                        price.save()
                        self.i += 1
                    else: 
                        continue
            self.max_page = self.page
        else:
            return
        
    def database_price_page(self):
        check_page = True
        while check_page:
            prices = MyPrice.objects.filter(page=self.page)
            if len(prices) == 0:
                self.page -= 1
            else:
                check_page = False
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

    def send_rows(self):
        prices = MyPrice.objects.filter(send=False)
        for price in prices:
            if self.i < 50:
                row = {
                    'detail' : price.detail,
                    'article' : price.article,
                    'price' : price.buyPrice,
                    'carreta' : price.carreta,
                    'amry' : price.amry,
                    'armtek' : price.armtek,
                    'emex' : price.emex
                }
                time.sleep(0.1)
                asyncio.run(self.send(json.dumps(row)))
                price.send = True
                price.page = self.page
                price.save()
                self.i += 1
            else:
                return
            
        return
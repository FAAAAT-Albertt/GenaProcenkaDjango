import json
import asyncio
import aiohttp
import aiofiles
import datetime
import requests
import time
import websocket

import pandas as pd

from ..models import MyPrice
from asgiref.sync import sync_to_async


async def parce_carreta(url, params, json_data):
    max_concurrent_requests = 1
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(max_concurrent_requests)
        async def fetch_data(session, url, pin):
            async with sem:
                params['q'] = pin.article
                async with session.get(url, params=params, ssl=False) as response:
                    return (await response.text(), pin)
        tasks = [fetch_data(session, url, json_data[i]) for i in range(len(json_data))]
        responses = await asyncio.gather(*tasks)
        for data, article in responses:
            task = asyncio.create_task(logics_operation(data, article))
            await task

async def logics_operation(response, article):
    # async def process_product(product):

#  if item['is_cross'] == False and item['period_max'] <= 15 and item['qty'].replace('>', '').replace('<', '').strip().isdigit() and int(item['qty'].replace('>', '').replace('<', '').strip()) > 1 and not item['stat'] is None and item['stat'] >= 85 and item['maker'].lower() == maker.lower()
#         if not product['is_cross'] is False or product['period_max'] > 15  or product['qty'] == "Есть" or int(product['qty'].replace('>', '').replace('<', '').strip()) < 2 or (not product['stat'] is None and product['stat'] < 85) or product is None or product['maker'].lower() != article.brand.lower().strip():
#             return {'price': 0}
#         else:
#             return {
#                     'brand': product['maker'],
#                     'name': product['name'],
#                     'code_source': product['source'],
#                     'quantity': product['qty'],
#                     'rating': product['stat'],
#                     'delivery': product['period_max'],
#                     'price': product['price'],
#                     # 'coef': round(float(product['stat'] / 100) * float(product['price']), 2)
                
#             }
#     tasks = []
    content = json.loads(response)
    originals = [item for item in content['objects'] if item['is_cross'] == False and item['period_max'] <= 15 and item['qty'].replace('>', '').replace('<', '').strip().isdigit() and int(item['qty'].replace('>', '').replace('<', '').strip()) > 1 and not item['stat'] is None and item['stat'] >= 85 and item['maker'].lower().strip() == article.brand.lower().strip()]

        # tasks.append(process_product(product))
    # processed_products = await asyncio.gather(*tasks)
    sorted_dict = sorted(originals, key=lambda item: float(item['price']))
    
    # result = {
    #     str(article): sorted_dict[0]
    # }
    # try:
    #     result_my = {
    #         'column' : 'carreta',
    #         'articul' : str(article),
    #         'price' : float(result[article]['price']),

    #     }
    #     ws = websocket.WebSocket()
    #     ws.connect("ws://127.0.0.1:8000/ws_detail")
    #     ws.send(json.dumps(result_my))
    #     ws.close()
    # except:
    #     pass
    if len(sorted_dict) > 0:
        await MyPrice.objects.filter(article = article.pk).aupdate(carreta = float(sorted_dict[0]['price']))
    else:
        await MyPrice.objects.filter(article = article.pk).aupdate(carreta = 0)

    # article.carreta = float(sorted_dict[0]['price'])
    # await article.asave()

async def main() -> None:
    start = time.monotonic()
    url = "https://api.carreta.ru/v1/search/"

    params = {
    "api_key": "d53b0932-3239-4ed9-9023-a3c49e6ca2cc",
    "q": ""
    }
    while True:
        prices = await get_all_support()
        if not prices:
            continue
        else:    
            await parce_carreta(url, params, prices)
            break
            # return time.monotonic() - start

@sync_to_async
def get_all_support() -> list:
    return list(MyPrice.objects.filter(send=False, carreta=0))

if __name__ == "__main__":
    print(asyncio.run(main()))


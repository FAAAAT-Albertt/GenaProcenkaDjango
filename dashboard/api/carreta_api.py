import json
import asyncio
import aiohttp
import aiofiles
import datetime
import requests
import time
import websocket


import pandas as pd

async def parce_carreta(url, params, json_data):
    max_concurrent_requests = 1
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(max_concurrent_requests)
        async def fetch_data(session, url, pin):
            async with sem:
                params['q'] = pin
                async with session.get(url, params=params, ssl=False) as response:
                    return (await response.text(), pin)
        tasks = [fetch_data(session, url, str(json_data[i]['Article'])) for i in range(len(json_data))]
        responses = await asyncio.gather(*tasks)
        for data, article in responses:
            task = asyncio.create_task(logics_operation(data, article))
            await task

async def logics_operation(response, article):
    async def process_product(product):  
        if not product['is_cross'] is False or product['period_max'] > 15  or product['qty'] == "Есть" or int(product['qty'].replace('>', '').replace('<', '').strip()) < 2 or (not product['stat'] is None and product['stat'] < 60):
            return {'coef': 0}
        else:
            return {
                    'brand': product['maker'],
                    'name': product['name'],
                    'code_source': product['source'],
                    'quantity': product['qty'],
                    'rating': product['stat'],
                    'delivery': product['period_max'],
                    'price': product['price'],
                    'coef': round(float(product['stat'] / 100) * float(product['price']), 2)
                
            }
    tasks = []
    content = json.loads(response)
    for product in content['objects']:
        tasks.append(process_product(product))
    processed_products = await asyncio.gather(*tasks)
    sorted_dict = sorted(processed_products, key=lambda item: (item['coef']==0, item['coef']))
    result = {
        str(article): sorted_dict[0]
    }
    try:
        result_my = {
            'column' : 'carreta',
            'articul' : str(article),
            'price' : float(result[article]['price']),

        }
        ws = websocket.WebSocket()
        ws.connect("ws://127.0.0.1:8000/ws_detail")
        ws.send(json.dumps(result_my))
        ws.close()
    except:
        pass

async def main() -> None:
    start = time.monotonic()
    url = "https://api.carreta.ru/v1/search/"

    params = {
    "api_key": "d53b0932-3239-4ed9-9023-a3c49e6ca2cc",
    "q": ""
    }
    column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
    df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
    json_data = df.to_dict(orient="records")
    await parce_carreta(url, params, json_data)
    return time.monotonic() - start


if __name__ == "__main__":
    print(asyncio.run(main()))


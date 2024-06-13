import json
import asyncio
import aiohttp
import aiofiles
import datetime
import time
import websocket

import pandas as pd

from ..models import MyPrice
from asgiref.sync import sync_to_async


async def armtek_parce(url, user_login, user_password, data, json_data) -> None:
    tasks = []
    max_concurrent_requests = 10

    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(max_concurrent_requests)
        async def fetch_data(session, url, data, obj):
            async with sem:
                data['PIN'] = obj.article
                data['BRAND'] = obj.brand.strip()
                async with session.post(url, data=data, auth=aiohttp.BasicAuth(user_login, user_password)) as response:
                    return (await response.text(), obj)  
        tasks = [fetch_data(session, url, data, json_data[i]) for i in range(len(json_data))]
        responses = await asyncio.gather(*tasks)
        for content, article in responses:
            task = asyncio.create_task(logics_operation(content, article))
            await task        
        
async def logics_operation(response, article):
    async def procces_product(product):
        if product == 'ERROR' or product == 'MSG': return {'price': 0}
        now_date = datetime.date.today()
        try:
            late_date = datetime.datetime.strptime(product['WRNTDT'], "%Y%m%d%H%M%S")
            fast_date = datetime.datetime.strptime(product['DLVDT'], "%Y%m%d%H%M%S")
            delivery_max = ((late_date.year - now_date.year) * 365) + ((late_date.month - now_date.month) * 30) + (late_date.day - now_date.day)
            delivery_min = ((fast_date.year - now_date.year) * 365) + ((fast_date.month - now_date.month) * 30) + (fast_date.day - now_date.day)
            if delivery_max > 15 and delivery_min > 15: return {'price': 0}
            elif delivery_max <= 15 and delivery_min < 15: delivery = delivery_max
            elif delivery_max > 15 and delivery_min <= 15: delivery = delivery_min
        except:
            late_date = datetime.datetime.strptime(product['DLVDT'], "%Y%m%d%H%M%S")
            delivery_min = ((late_date.year - now_date.year) * 365) + ((late_date.month - now_date.month) * 30) + (late_date.day - now_date.day)
            if delivery_min > 15: return {'price': 0}
            else: delivery = delivery_min
        if int(product['RVALUE'].replace('>', '').replace('<', '').strip()) < 2 or int(float(product['VENSL'])) < 85:
            return {
                'price': 0
            }
        else:
            return {
                'brand': product['BRAND'],
                'name': product['NAME'],
                'quantity': product['RVALUE'].replace('>', '').replace('<', '').strip(),
                'delivery': str(delivery),
                'rating': product['VENSL'],
                'price': product['PRICE'],
                # 'coef': round((int(float(product['VENSL'])) / 100) * float(product['PRICE']), 2)
            }

    content = json.loads(response)
    tasks = []
    for product in content['RESP']:
        tasks.append(procces_product(product))
    processed_products = await asyncio.gather(*tasks)
    sorted_dict = sorted(processed_products, key=lambda item: (item['price']==0, float(item['price'])))
    
    # result = {
    #     str(article): sorted_dict[0]
    # }
    # try:
    #     result_my = {
    #         'column' : 'armtek',
    #         'articul' : str(article),
    #         'price' : float(result[article]['price']),

    #     }
    #     ws = websocket.WebSocket()
    #     ws.connect("ws://127.0.0.1:8000/ws_detail")
    #     ws.send(json.dumps(result_my))
    #     ws.close()
    # except:
    #     pass
    
    # try:
    await MyPrice.objects.filter(article = article.pk).aupdate(armtek = float(sorted_dict[0]['price']))
    # except:
    #     await MyPrice.objects.filter(article = article.pk).aupdate(armtek = 0)

    # article.armtek = float(sorted_dict[0]['price'])
    # await article.asave()

    # async with aiofiles.open('json_parce/api_armtek.json', 'a+', encoding='utf-8') as file:
    #     await file.write(json.dumps(result, indent=4, ensure_ascii=False))


async def main() -> None:
    start = time.monotonic()
    url = "http://ws.armtek.ru/api/ws_search/search?format=json"
    user_login = "ZAKUP@MIGEDIKI.RU"
    user_password = "gesha221287"
    data = {
        'VKORG': "4000",
        'KUNNR_RG': "43052930",
        'PIN': '',
        'BRAND': '',
        'QUERY_TYPE': '1',
        'PROGRAM': '',
        'KUNNR_ZA': '',
        'VBELN': ''
    }
    # column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
    # df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
    # json_data = df.to_dict(orient="records")
    # await armtek_parce(url, user_login, user_password, data, json_data)
    # return time.monotonic() - start

    while True:
        prices = await get_all_support()
        if not prices:
            continue
        else:    
            await armtek_parce(url, user_login, user_password, data, prices)
            break
            # return time.monotonic() - start

@sync_to_async
def get_all_support() -> list:
    return list(MyPrice.objects.filter(send=False, armtek=0))

if __name__ == '__main__':
    print(asyncio.run(main()))
import requests
import asyncio
import aiohttp
import pandas as pd

from datetime import datetime
import json

from ..models import MyPrice
from asgiref.sync import sync_to_async

async def parce_favorit(articles):
    tasks = []
    max_concurrent_requests = 10
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(max_concurrent_requests)
        async def fetch_data(session, article):
            async with sem:
                try:
                    url = "http://api.favorit-parts.ru/hs/hsprice/"
                    params = {
                        "key": "32761F6E-AA11-4090-AD68-06C648A05C14",
                        "number": article.article,
                        "brand": article.brand.strip(),
                        "info": "on",
                    }
                    async with session.get(url, params=params, ssl=False) as response:
                        return (await response.json(), article)
                except Exception as ex:
                    print(f"[INFO] - {ex}")
        tasks = [fetch_data(session, articles[i]) for i in range(len(articles))]
        responses = await asyncio.gather(*tasks)
        for content, article in responses:
            task = asyncio.create_task(logics_operation(content, article))
            await task   


async def logics_operation(content, article):
    async def check_date(date):
        date_time_obj = datetime.fromisoformat(date.split('T')[0]).date()
        today = datetime.now().date()
        difference = date_time_obj - today
        return difference.days
    result = [data for data in content['goods'][0]['warehouses'] if data['stock'] > 1 and await check_date(data['shipmentDate']) <= 15]
    sorted_dict = sorted(result, key=lambda item: (item['price']==0, float(item['price'])))
    if len(sorted_dict) != 0:
        await MyPrice.objects.filter(article = article.pk).aupdate(favorit = float(sorted_dict[0]['price']), favorit_done = True)
            
    
async def main():
    prices = await get_all_support()
    await parce_favorit(prices)
    


@sync_to_async
def get_all_support() -> list:
    return list(MyPrice.objects.filter(send=False, favorit=0))

if __name__ == "__main__":
    asyncio.run(main())
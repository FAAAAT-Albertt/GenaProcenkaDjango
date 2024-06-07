import json
import asyncio
import aiohttp
import aiofiles
import datetime
import websocket

import pandas as pd
import time

async def amry_parce(url, headers, cookies, params, json_data, start) -> None:
    max_concurrent_requests = 10
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(max_concurrent_requests)
        async def fetch_data(session, url, pin, brand):
            async with sem:
                params['article'] = pin
                params['brand'] = brand
                async with session.get(url, headers=headers, cookies=cookies, params=params, ssl=False) as response:
                    print(response.status)
                    return (await response.text(), pin)
                    
        tasks = [fetch_data(session, url, str(json_data[i]['Article']), json_data[i]['Brand']) for i in range(len(json_data))]
        responses = await asyncio.gather(*tasks)
        for data, article in responses:
            task = asyncio.create_task(logics_operation(data, article))
            await task
    return time.monotonic() - start
async def logics_operation(response, article):
    async def process_product(product):
        if product['amountNum'] < 2 or product['termMax'] > 15 or float(product['rating']) < 3.4:
            return {'coef': 0}
        else:
            return {
                'id': product['id'],
                'brand': product['brand'],
                'name': product['name'],
                'amount': product['amount'],
                'delivery': product['termMax'],
                'rating': product['rating'],
                'price': product['price'],
                'coef': (float(product['rating']) / 100) * float(product['price'])
            }

    tasks = []
    content = json.loads(response)
    for product in content['data']['rows']['request']:
        tasks.append(process_product(product))
    processed_products = await asyncio.gather(*tasks)
    sorted_dict = sorted(processed_products, key=lambda item: (item['coef']==0, item['coef']))
    result = {
        str(article): sorted_dict[0]
    }
    try:
        result_my = {
            'column' : 'amry',
            'articul' : str(article),
            'price' : float(result[article]['price']),

        }
        ws = websocket.WebSocket()
        ws.connect("ws://127.0.0.1:8000/ws_detail")
        ws.send(json.dumps(result_my))
        ws.close()
    except:
        pass
    # async with aiofiles.open('json_parce/api_amry.json', 'a+', encoding='utf-8') as file:
    #     await file.write(json.dumps(result, indent=4, ensure_ascii=False))

async def main() -> None:
    url = "https://www.amry.ru/api/v2/client/search/"
    cookies = {
        'PHPSESSID': '6058eabca59151680d715ab62a169386',
        'force_stock_id': '1',
        '_ym_uid': '1715744514147827437',
        '_ym_d': '1715744514',
        # '_gid': 'GA1.2.767484036.1715947064',
        'cid': '1',
        'CLIENT': '3667%3Aa98f2df1ac59fbd9c99634c96749f6af109bf606',
        '_ga': 'GA1.2.413840589.1715744514',
        '_ga_MMGXDW9XLG': 'GS1.1.1715947064.2.1.1715947250.0.0.0',
        'NOTICE_USE_COOKIE': '1',
        '_ym_isad': '2',
        '_ym_visorc': 'w',
        'cid': '1',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': 'PHPSESSID=f9cbd57d064b855172df325d9390d2e5; force_stock_id=1; _ym_uid=1715744514147827437; _ym_d=1715744514; _gid=GA1.2.767484036.1715947064; cid=1; CLIENT=3667%3Aa98f2df1ac59fbd9c99634c96749f6af109bf606; _ga=GA1.2.413840589.1715744514; _ga_MMGXDW9XLG=GS1.1.1715947064.2.1.1715947250.0.0.0; NOTICE_USE_COOKIE=1; _ym_isad=2; _ym_visorc=w',
        'priority': 'u=1, i',
        'referer': 'https://www.amry.ru/search.html?article=1429840&brand=FORD&withAnalogs=0',
        # 'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'warlng': 'undefined',
    }
    params = {
        'article': '1429849',
        'brand': 'FORD',
        'withAnalogs': '0',
    }
    column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
    df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
    json_data = df.to_dict(orient="records")
    print(await amry_parce(url, headers, cookies, params, json_data, time.monotonic()))

if __name__ == "__main__":
    asyncio.run(main())
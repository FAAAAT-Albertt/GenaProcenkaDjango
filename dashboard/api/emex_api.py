import asyncio
import httpx
from zeep import AsyncClient
from zeep.transports import AsyncTransport
from zeep.helpers import serialize_object
import aiofiles
import json
import websocket

import pandas as pd

async def emex_parce(article) -> None:
    login = "2742407"
    password = "8f228f39"
    make_logo = None
    detail_num = str(article)
    subst_level = 'OriginalOnly'
    subst_filter = 'FilterOriginalAndAnalogs'
    delivery_region_type = 'PRI'
    min_delivery_percent = '60.00'
    max_ad_days = 15
    min_quantity = 2
    max_result_price = None
    max_one_detail_offers_count = None
    detail_nums_to_load = None

    httpx_client = httpx.AsyncClient(auth=(login, password))
    async with AsyncClient('http://ws.emex.ru/EmExService.asmx?WSDL', transport=AsyncTransport(httpx_client)) as client:
        response = await client.service.FindDetailAdv4(
            login=login,
            password=password,
            makeLogo=make_logo,
            detailNum=detail_num,
            substLevel=subst_level,
            substFilter=subst_filter,
            deliveryRegionType=delivery_region_type,
            minDeliveryPercent=min_delivery_percent,
            maxADDays=max_ad_days,
            minQuantity=min_quantity,
            maxResultPrice=max_result_price,
            maxOneDetailOffersCount=max_one_detail_offers_count,
            detailNumsToLoad=detail_nums_to_load
        )
        content = serialize_object(response) 
        result = [
            {
            'brand': product['MakeName'],
            'name': product['DetailNameRus'],
            'quantity': product['Quantity'],
            'delivery': product['ADDays'],
            'rating': float(product['DDPercent']),
            'price': float(product['ResultPrice']),
            'coef': round((float(product['DDPercent']) / 100) * float(product['ResultPrice']), 2)
            } for product in content['Details']['SoapDetailItem']
        ]
        sorted_dict = sorted(result, key=lambda item: item['coef'])
        result = {
            detail_num: sorted_dict[0]
        }
        try:
            result_my = {
                'column' : 'emex',
                'articul' : str(article),
                'price' : float(result[article]['price']),

            }
            ws = websocket.WebSocket()
            ws.connect("ws://127.0.0.1:8000/ws_detail")
            ws.send(json.dumps(result_my))
            ws.close()
        except:
            pass
    pass

async def main():
    column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
    df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
    json_data = df.to_dict(orient="records")
    tasks = [emex_parce(json_data[i]['Article']) for i in range(len(json_data))]
    await asyncio.gather(*tasks)
    
if __name__ == "__main__":
    asyncio.run(main())

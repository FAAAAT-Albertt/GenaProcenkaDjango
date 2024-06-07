import asyncio
from ftplib import FTP
import pandas as pd
import numpy as np

from ...models import DetailAmry
from django.core.management.base import BaseCommand

class Command(BaseCommand):
   # Используется как описание команды обычно
    help = 'Just a command for launching Backend'

    def handle(self, *args, **kwargs):
        # asyncio.run(self.database_work())
        self.database_work()
        
    def database_work(self):
        # for file in ['Amry2', 'Amry4', 'Amry6']:
        for file in ['Amry4', 'Amry6']:
            df = pd.read_csv(f'temp_files/{file}.csv',delimiter=';', encoding='cp1251')
            result = df.to_numpy()
            DetailAmry.objects.bulk_create([DetailAmry(
                detail=data_detail[2],
                article=data_detail[1],
                brand=data_detail[0],
                quantity=int(round(float(str(data_detail[3]).replace(',','.')))),
                price=float(data_detail[4].replace(",", ".")),
                part=data_detail[5],
            ) for data_detail in np.array(result)])
            # for data_detail in np.array(result):
                # detail = await DetailAmry.objects.acreate(
                #     detail=data_detail[2],
                #     article=data_detail[1],
                #     brand=data_detail[0],
                #     quantity=data_detail[3],
                #     price=float(data_detail[4].replace(",", ".")),
                #     part=data_detail[5],
                # )
                # await detail.asave()


    def ftp_down(self):
        try:
            ftp = FTP(host='amry.ru')
            ftp.encoding='utf-8'
            ftp.login(user='amry_prices', passwd='77pmf4BkzH')
            for file_name in ['Amry2', 'Amry4', 'Amry6']:
                with open(f'temp_files/{file_name}.csv', 'wb') as file:
                    ftp.retrbinary(f"RETR {file_name}.csv", file.write)
            ftp.quit()
        except Exception as ex:
            print(ex)
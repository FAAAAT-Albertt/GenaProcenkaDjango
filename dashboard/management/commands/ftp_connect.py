from ftplib import FTP
import pandas as pd
import numpy as np

from ...models import DetailAmry
from django.core.management.base import BaseCommand

class Command(BaseCommand):
   # Используется как описание команды обычно
    help = 'Just a command for launching Backend'

    def handle(self, *args, **kwargs):
        self.database_work()
        
    def database_work(self):
        for file in ['Amry2', 'Amry4', 'Amry6']:
            df = pd.read_csv(f'temp_files/{file}.csv',delimiter=';', encoding='cp1251')
            result = df.to_numpy()
            for data_detail in np.array(result):
                detail = DetailAmry.objects.create(
                    detail=data_detail[2],
                    article=data_detail[1],
                    brand=data_detail[0],
                    quantity=data_detail[3],
                    price=float(data_detail[4].replace(",", ".")),
                    part=data_detail[5],
                )
                detail.save()

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
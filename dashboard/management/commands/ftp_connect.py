import asyncio
from ftplib import FTP
import pandas as pd
import numpy as np
import schedule
import time
import pytz
from datetime import datetime
from threading import Thread

from ...models import DetailAmry
from django.core.management.base import BaseCommand

class Command(BaseCommand):
   # Используется как описание команды обычно
    help = 'Just a command for launching Backend'

    def handle(self, *args, **kwargs):
        # asyncio.run(self.database_work())

        scheduler_thread = Thread(target=self.schedule_job)
        scheduler_thread.start()
    
    def schedule_job(self):
        novosibirsk_tz = pytz.timezone('Asia/Novosibirsk')
        now = datetime.now(novosibirsk_tz)

        next_run_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run_time:
            next_run_time = next_run_time.replace(day=now.day + 1)
        
        time_to_wait = (next_run_time - now).total_seconds()
        print(f"Next run in {time_to_wait} seconds")
        
        schedule.every(time_to_wait).seconds.do(self.ftp_down)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def database_work(self):
        # for file in ['Amry2', 'Amry4', 'Amry6']:
        DetailAmry.objects.all().delete()
        for file in ['Amry2' 'Amry4', 'Amry6']:
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

    def ftp_down(self):
        try:
            ftp = FTP(host='amry.ru')
            ftp.encoding='utf-8'
            ftp.login(user='amry_prices', passwd='77pmf4BkzH')
            for file_name in ['Amry2', 'Amry4', 'Amry6']:
                with open(f'temp_files/{file_name}.csv', 'wb') as file:
                    ftp.retrbinary(f"RETR {file_name}.csv", file.write)
            ftp.quit()

            self.database_work()
        except Exception as ex:
            print(ex)





import asyncio
from django.core.management.base import BaseCommand
from ...api import emex_api

class Command(BaseCommand):
   # Используется как описание команды обычно
    help = 'Just a command for launching Backend'

    def handle(self, *args, **kwargs):
        asyncio.run(emex_api.main())
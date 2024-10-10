"""
ASGI config for setup project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

import django
from django.core.asgi import get_asgi_application
from django.urls import path

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

application = get_asgi_application()
django_asgi_app = get_asgi_application()

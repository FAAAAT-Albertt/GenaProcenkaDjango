from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import DetailAmry, IsCompletedProducts


import json
import os
import pandas as pd

# Create your views here.
class LoginView(TemplateView):
    template_name = "login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/dashboard")
        if request.method == 'GET':
            return render(request, self.template_name)

        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is None:
                context = {
                    "error": "Неверные логин или пароль"
                }
                return render(request, self.template_name, context)

            login(request, user)
            return redirect("/dashboard")
        
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        if request.method == 'GET':
            column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
            df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
            json_data = df.to_dict(orient="records")
        
            return render(request, self.template_name, context={"details" : json_data})
        
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    if 'file' not in request.data:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    file_obj = request.data['file']
    valid_mime_types = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    
    if file_obj.content_type not in valid_mime_types:
        return Response({'error': 'Invalid file type. Please upload an Excel file.'}, status=status.HTTP_400_BAD_REQUEST)
    
    save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_obj.name)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    
    return Response({'message': 'Файл успешно загружен!', 'file_path': save_path}, status=status.HTTP_201_CREATED)

@csrf_exempt
def upload_completed_products(request):
    if request.method == 'POST':
        try:
            file = request.FILES['file']
            file_content = file.read().decode('utf-8')
            data = json.loads(file_content)
            print(data)
            save_completed_products(data)
            return JsonResponse({'message': 'Данные успешно сохранены!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


async def save_completed_products(data):
    pass
    column_names = ["Detail", "Article", "Brand", "BuyPrice", "Unnamed: 4", "SalePrice"]
    df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
    json_data = df.to_dict(orient="records")

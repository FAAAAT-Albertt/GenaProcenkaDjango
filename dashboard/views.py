from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import IsCompletedProducts, MyPrice

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
            # df = pd.read_excel("dashboard/base_procenka.xlsx", names=column_names, usecols=lambda x: x not in 'Unnamed: 4')
            # json_data = df.to_dict(orient="records")
            json_data = []
        
            return render(request, self.template_name, context={"details" : json_data})
        
@api_view(['POST'])
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

    update_base_my_price()

    return Response({'message': 'Файл успешно загружен!', 'file_path': save_path}, status=status.HTTP_201_CREATED)

def update_base_my_price():
    # , usecols=lambda x: x not in 'Unnamed: 4' names=column_names
    column_names = ["Detail", "Article", "Brand", "BuyPrice", "SalePrice"]
    df = pd.read_excel("media/uploads/base_procenka.xlsx", names=column_names, skiprows=1)
    filtered_df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    json_data = df.to_dict(orient="records")

    MyPrice.objects.all().delete()

    MyPrice.objects.bulk_create([MyPrice(
            detail = data['Detail'],
            brand = data['Brand'],
            article = data['Article'],
            buyPrice = float(data['BuyPrice']),
            salePrice = float(data['SalePrice'])
            ) for data in json_data])

@api_view(['POST'])
def upload_completed_products(request, format=None):
    try:
        data = request.data
        print(data)
        save_completed_products(data)
        return JsonResponse({'message': 'Данные успешно сохранены!'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def save_completed_products(data):
    for detail in data:
        try:
            products = MyPrice.objects.get(article=detail[0])
        except MyPrice.DoesNotExist:
            continue

        IsCompletedProducts.objects.create(
            detail_data=products,
            # price=detail[1]
            price=4444.44
        ).save()

def export_to_excel(request):
    # Извлечение данных из модели
    result = []
    details_price = IsCompletedProducts.objects.all().values()
    
    for detail_price in details_price:
        try:
            detail_enother = MyPrice.objects.get(article=detail_price['detail_data_id'])
            result.append({
                "detail": detail_enother.detail,
                "article": detail_enother.article,
                "brand": detail_enother.brand,
                "price": detail_price['price']
            })
        except MyPrice.DoesNotExist:
            continue

    # Создание DataFrame
    df = pd.DataFrame(result)
    
    # Указание директории для сохранения файла
    directory = 'exported_files'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, 'details.xlsx')
    
    # Сохранение DataFrame в Excel файл
    df.to_excel(file_path, index=False)
    
    # Создание HTTP ответа с Excel файлом
    with open(file_path, 'rb') as excel:
        response = HttpResponse(excel.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
        IsCompletedProducts.objects.all().delete()
        return response



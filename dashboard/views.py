from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

import json
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
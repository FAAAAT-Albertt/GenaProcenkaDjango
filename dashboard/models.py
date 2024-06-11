from django.db import models

class DetailAmry(models.Model):
    """таблица выгрузки запчастей amry"""
    detail = models.CharField(max_length=200, blank=False)
    article = models.CharField(max_length=50, blank=False)
    brand = models.CharField(max_length=50, blank=False)
    quantity = models.IntegerField(blank=False)
    price = models.FloatField(blank=False)
    part = models.IntegerField(blank=False)

class IsCompletedProducts(models.Model):
    """Проценненые товары"""
    detail_data = models.ForeignKey("MyPrice", on_delete=models.CASCADE)
    price = models.FloatField(blank=False)

class MyPrice(models.Model):
    """таблиц своих товаров для проценки"""
    detail = models.CharField(blank=False)
    brand = models.CharField(blank=False)
    article = models.CharField(blank=False, primary_key=True)
    buyPrice = models.FloatField(blank=False)
    salePrice = models.FloatField(blank=False)
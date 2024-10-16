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
    favorit = models.FloatField(blank=False, default=0)
    favorit_done = models.BooleanField(default=False)
    amry = models.FloatField(blank=False, default=0)
    amry_done = models.BooleanField(default=False)
    armtek = models.FloatField(blank=False, default=0)
    armtek_done = models.BooleanField(default=False)
    emex = models.FloatField(blank=False, default=0)
    emex_done = models.BooleanField(default=False)
    send = models.BooleanField(default=False)
    page = models.PositiveSmallIntegerField(default=0)
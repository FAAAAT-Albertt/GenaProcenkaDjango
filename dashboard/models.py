from django.db import models

class DetailAmry(models.Model):
    """таблица выгрузки запчастей amry"""
    detail = models.CharField(max_length=200, blank=False)
    article = models.CharField(max_length=50, blank=False)
    brand = models.CharField(max_length=50, blank=False)
    quantity = models.IntegerField(blank=False)
    price = models.FloatField(blank=False)
    part = models.IntegerField(blank=False)

    class Meta:
        indexes = [
            models.Index(fields=['article', 'quantity'], name='article_quantity_idx'),
        ]
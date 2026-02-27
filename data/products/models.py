from django.db import models
from data.whouse.models import Whouse
from apps.common.models import BaseModel

class ProductType(BaseModel):
    name = models.CharField(max_length=255)
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class ProductUnit(BaseModel):
    name = models.CharField(max_length=255)
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(BaseModel):
    name = models.CharField(max_length=255)
    types = models.ManyToManyField(ProductType, related_name='products')
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

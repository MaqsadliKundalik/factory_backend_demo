from django.db import models
from data.whouse.models import Whouse
from apps.common.models import BaseModel
from data.filedatas.models import File

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

class WhouseProducts(BaseModel):
    """
    PENDING - qorovul qoshsa tushadigan status
    CREATED - skladchi qo’shsa tushadigan status
    REJECTED - skladchi qorovul qo’shgan mahsulotni rad etsa chiqadigan status
    CONFIRMED - skladchi qorovul qo'shgan mahsulotni tasdiqlaydi
    """
    STATUSES = [
        ('pending', 'Pending'),
        ('created', 'Created'),
        ('rejected', 'Rejected'),
        ('confirmed', 'Confirmed'),
    ]
    
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    files = models.ManyToManyField(File, related_name='whouse_products')
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    
    def __str__(self):
        return self.product.name
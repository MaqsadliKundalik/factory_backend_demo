from django.db import models
from apps.common.models import BaseModel
from data.filedatas.models import File
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from data.notifications.models import Notification
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.supplier.models import Supplier
    from data.users.models import FactoryUser


class HistoryStatus(models.TextChoices):
    IN = 'IN', 'In'
    OUT = 'OUT', 'Out'

class ProductType(BaseModel):
    name = models.CharField(max_length=255)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class ProductUnit(BaseModel):
    name = models.CharField(max_length=255)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Product(BaseModel):
    name = models.CharField(max_length=255)
    types = models.ManyToManyField(ProductType, related_name='products')
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
class ProductItem(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    raw_material = models.ForeignKey('products.WhouseProducts', on_delete=models.CASCADE, related_name='used_in', null=True, blank=True)
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class WhouseProducts(BaseModel):
    """
    PENDING - qorovul qoshsa tushadigan status
    CREATED - skladchi qo’shsa tushadigan status
    REJECTED - skladchi qorovul qo’shgan mahsulotni rad etsa chiqadigan status
    CONFIRMED - skladchi qorovul qo'shgan mahsulotni tasdiqlaydi
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CREATED = 'CREATED', 'Created'
        REJECTED = 'REJECTED', 'Rejected'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
    
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    supplier: "Supplier | None" = models.ForeignKey('supplier.Supplier', on_delete=models.CASCADE, null=True, blank=True)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    files = models.ManyToManyField('filedatas.File', blank=True, related_name='whouse_product_files')
    creator : "FactoryUser | None" = models.ForeignKey("users.FactoryUser", on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.product.name

class WhouseProductsHistory(BaseModel):
    wproduct = models.ForeignKey("products.WhouseProducts", on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey('supplier.Supplier', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=HistoryStatus.choices, default=HistoryStatus.IN)

    def __str__(self):
        return f"History of {self.product.name} at {self.created_at}"


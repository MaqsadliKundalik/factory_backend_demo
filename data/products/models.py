from django.db import models
from apps.common.models import BaseModel
from data.filedatas.models import File
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from data.notifications.models import Notification

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
    name = models.CharField(max_length=255)
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
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    files = models.ManyToManyField(File, related_name='whouse_products')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    def __str__(self):
        return self.product.name

class WhouseProductsHistory(BaseModel):

    product = models.ForeignKey("data.products.Product", on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=HistoryStatus.choices, default=HistoryStatus.IN)

    def __str__(self):
        return f"History of {self.product.name} at {self.created_at}"

# Signals for history tracking

@receiver(post_save, sender=WhouseProducts)
def create_whouse_product_history(sender, instance, **kwargs):
    if instance.status == WhouseProducts.Status.PENDING:
        Notification.objects.create(
            to_role='whouse_manager',
            from_role='guard',
            title='New product added',
            message=f'New product {instance.product.name} added to whouse {instance.whouse.name}',
        )   


    WhouseProductsHistory.objects.create(
        whouse=instance.whouse,
        product=instance.product,
        quantity=instance.quantity,
        status=HistoryStatus.IN
    )

@receiver(post_save, sender=ProductItem)
def update_whouse_product_history(sender, instance, **kwargs):
    if instance.status == ProductItem.Status.CREATED:
        WhouseProductsHistory.objects.create(
            whouse=instance.product.whouse,
            product=instance.product,
            quantity=instance.quantity,
            status=HistoryStatus.OUT
        )



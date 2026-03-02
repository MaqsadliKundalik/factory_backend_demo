from django.db import models
from data.whouse.models import Whouse
from apps.common.models import BaseModel
from data.filedatas.models import File
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from data.notifications.models import Notification


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

class WhouseProductsHistory(BaseModel):
    whouse_product = models.ForeignKey(WhouseProducts, on_delete=models.CASCADE, related_name='history', null=True, blank=True)
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    files = models.ManyToManyField(File, related_name='whouse_products_history')
    status = models.CharField(max_length=20, choices=WhouseProducts.STATUSES, default='pending')
    
    def __str__(self):
        return f"History of {self.product.name} at {self.created_at}"

# Signals for history tracking

@receiver(post_save, sender=WhouseProducts)
def create_whouse_product_history(sender, instance, **kwargs):
    if instance.status == 'pending':
        Notification.objects.create(
            to_role='whouse_manager',
            from_role='guard',
            title='New product added',
            message=f'New product {instance.product.name} added to whouse {instance.whouse.name}',
        )


    history = WhouseProductsHistory.objects.create(
        whouse_product=instance,
        whouse=instance.whouse,
        product=instance.product,
        quantity=instance.quantity,
        status=instance.status
    )
    if instance.pk:
        history.files.set(instance.files.all())

@receiver(m2m_changed, sender=WhouseProducts.files.through)
def update_history_files(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        latest_history = instance.history.first()
        if latest_history:
            latest_history.files.set(instance.files.all())
from typing import TYPE_CHECKING

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.common.models import BaseModel


if TYPE_CHECKING:
    from data.products.models import ProductType, ProductUnit, Product
    from data.filedatas.models import File
    from data.clients.models import Client, ClientBranches
    from apps.drivers.models import Driver
    from data.transports.models import Transport
    from data.whouse.models import Whouse


# Create your models here.
class Order(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CREATED = 'CREATED', 'Created'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    display_id = models.PositiveIntegerField(unique=True, editable=False, null=True)
    client:"Client" = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name='orders')
    branch:"ClientBranches" = models.ForeignKey("clients.ClientBranches", on_delete=models.CASCADE, related_name='orders')
    whouse:"Whouse" = models.ForeignKey("factory_whouse.Whouse", on_delete=models.CASCADE, related_name='orders')
    product:"Product" = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='orders')
    type:"ProductType" = models.ForeignKey("products.ProductType", on_delete=models.CASCADE, related_name='orders')
    unit:"ProductUnit" = models.ForeignKey("products.ProductUnit", on_delete=models.CASCADE, related_name='orders')    
    external_drivers = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def save(self, *args, **kwargs):
        if not self.display_id:
            last_order = Order.objects.all().order_by('display_id').last()
            self.display_id = (last_order.display_id + 1) if last_order and last_order.display_id else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ord-{self.display_id:03}" if self.display_id else f"Ord-{self.id}"

class SubOrder(BaseModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CREATED = 'CREATED', 'Created'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sub_orders')
    driver = models.ForeignKey("factory_drivers.Driver", on_delete=models.CASCADE, related_name='sub_orders')
    transport = models.ForeignKey("transports.Transport", on_delete=models.CASCADE, related_name='sub_orders')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    files = models.ManyToManyField("filedatas.File", related_name='sub_orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    status_history = models.JSONField(default=list)

    def __str__(self):
        display_name = f"Ord-{self.order.display_id:03}" if self.order.display_id else f"Ord-{self.order.id}"
        return f"SubOrd-{self.id} for {display_name}"

@receiver(post_save, sender=SubOrder)
def update_whouse_product_history(sender, instance, **kwargs):
    if instance.status == SubOrder.Status.CREATED:
        from django.apps import apps
        WhouseProductsHistory = apps.get_model('products', 'WhouseProductsHistory')
        WhouseProductsHistory.objects.create(
            whouse=instance.order.whouse,
            product=instance.order.product,
            quantity=instance.quantity,
            status='OUT'  # HistoryStatus.OUT
        )


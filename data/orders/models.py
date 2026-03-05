from typing import TYPE_CHECKING

from django.db import models
from apps.common.models import BaseModel


if TYPE_CHECKING:
    from data.products.models import ProductType, ProductUnit, Product, WhouseProductsHistory, HistoryStatus
    from data.filedatas.models import File
    from data.clients.models import Client, ClientBranches
    from apps.drivers.models import Driver
    from data.transports.models import Transport
    from data.whouse.models import Whouse


# Create your models here.
class Order(BaseModel):
    display_id = models.IntegerField(primary_key=True)
    client:"Client" = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name='orders')
    branch:"ClientBranches" = models.ForeignKey("clients.ClientBranches", on_delete=models.CASCADE, related_name='orders')
    whouse:"Whouse" = models.ForeignKey("factory_whouse.Whouse", on_delete=models.CASCADE, related_name='orders')
    product:"Product" = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='orders')
    type:"ProductType" = models.ForeignKey("products.ProductType", on_delete=models.CASCADE, related_name='orders')
    unit:"ProductUnit" = models.ForeignKey("products.ProductUnit", on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=Order.Status.choices, default=Order.Status.PENDING)
    
    def __str__(self):
        return f"Ord-{self.display_id:03}"

class SubOrder(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sub_orders')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='sub_orders')
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='sub_orders')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    files = models.ManyToManyField(File, related_name='sub_orders')
    status = models.CharField(max_length=20, choices=SubOrder.Status.choices, default=SubOrder.Status.PENDING)
    
    def __str__(self):
        return f"SubOrd-{self.id} for Ord-{self.order.display_id:03}"

@receiver(post_save, sender=SubOrder)
def update_whouse_product_history(sender, instance, **kwargs):
    if instance.status == SubOrder.Status.CREATED:
        WhouseProductsHistory.objects.create(
            whouse=instance.order.whouse,
            product=instance.order.product,
            quantity=instance.quantity,
            status=HistoryStatus.OUT
        )


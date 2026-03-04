from django.db import models
from apps.common.models import BaseModel
from data.products.models import ProductType, ProductUnit, Product
from data.filedatas.models import File
from data.clients.models import Client, ClientBranches
from apps.drivers.models import Driver
from data.transports.models import Transport
from data.whouse.models import Whouse

# Create your models here.
class Order(BaseModel):
    display_id = models.IntegerField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    branch = models.ForeignKey(ClientBranches, on_delete=models.CASCADE, related_name='orders')
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='orders')
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='orders')
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
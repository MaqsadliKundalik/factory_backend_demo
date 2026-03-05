from typing import TYPE_CHECKING

from django.db import models
from data.filedatas.models import File
from apps.common.models import BaseModel

if TYPE_CHECKING:
    from data.orders.models import Order


class Client(BaseModel):
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=9)
    phone_number = models.CharField(max_length=255)
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE)
    
    list_display = ["name", "inn_number", "phone_number", "whouse"]


    orders: "models.QuerySet[Order]" 

    def __str__(self):
        return self.name

class ClientBranches(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()
    
    list_display = ["client", "name", "address", "longitude", "latitude"]
    
    def __str__(self):
        return f"{self.name} - {self.client}"
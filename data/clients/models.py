from django.db import models
from apps.common.models import BaseModel
    
# Create your models here.
class Client(BaseModel):
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=55)
    phone_number = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE)
    
    list_display = ["name", "inn_number", "phone_number", "whouse"]
    
    def __str__(self):
        return self.name

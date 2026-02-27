from django.db import models
from apps.common.models import BaseModel
from apps.whouse.models import Whouse
    
# Create your models here.
class Client(BaseModel):
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=55)
    phone_number = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

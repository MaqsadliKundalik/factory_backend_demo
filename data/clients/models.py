from django.db import models
from apps.common.models import BaseModel
from data.users.models import FactoryUser    
# Create your models here.
class Client(BaseModel):
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=9)
    phone_number = models.CharField(max_length=255)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE)
    
    list_display = ["name", "inn_number", "phone_number", "whouse"]
    
    def __str__(self):
        return self.name

class UserBranches(BaseModel):
    user = models.ForeignKey(FactoryUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE)
    
    list_display = ["user", "whouse"]
    
    def __str__(self):
        return f"{self.name} - {self.user}"
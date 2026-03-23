from django.db import models
from apps.common.models import BaseModel

class Transport (BaseModel):
    class Type(models.TextChoices):
        INTERNAL = 'INTERNAL', 'Internal'
        EXTERNAL = 'EXTERNAL', 'External'

    class CarType(models.TextChoices):
        EXCAVATOR = 'EXCAVATOR', 'Excavator'
        TRUCK = 'TRUCK', 'Truck'
    
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=Type.choices, default=Type.INTERNAL)
    car_type = models.CharField(max_length=100, choices=CarType.choices, default=CarType.TRUCK)
    number = models.CharField(max_length=100)
    
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.number
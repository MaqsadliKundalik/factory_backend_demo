from django.db import models
from apps.common.models import BaseModel

class Transport (BaseModel):
    TYPE_CHOICES = (
        ('EXCAVATOR', 'Excavator'),
        ('TRUCK', 'Truck'),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    number = models.CharField(max_length=100)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.number
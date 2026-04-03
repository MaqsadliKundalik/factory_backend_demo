from django.db import models
from apps.common.models import BaseModel
from data.orders.models import SubOrder
from django.utils import timezone


class Transport(BaseModel):
    class Type(models.TextChoices):
        INTERNAL = "INTERNAL", "Internal"
        EXTERNAL = "EXTERNAL", "External"

    class CarType(models.TextChoices):
        EXCAVATOR = "EXCAVATOR", "Excavator"
        TRUCK = "TRUCK", "Truck"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=Type.choices, default=Type.INTERNAL)
    car_type = models.CharField(
        max_length=100, choices=CarType.choices, default=CarType.TRUCK
    )
    number = models.CharField(max_length=100)

    whouse = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name + " " + self.number

    def delete(self, using=None, keep_parents=False):
        if not SubOrder.objects.filter(transport=self).exclude(status__in=[SubOrder.Status.REJECTED, SubOrder.Status.COMPLETED]).exists():
            self.deleted_at = timezone.now()
            self.save(update_fields=['deleted_at'])
        else:
            raise ValueError("Transport is used in suborders")




    
    class Meta:
        unique_together = ["number", "whouse"]

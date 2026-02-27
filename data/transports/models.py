from django.db import models
from apps.common.models import BaseModel

class Transport (BaseModel):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(TransportType, on_delete=models.CASCADE)
    number = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.number
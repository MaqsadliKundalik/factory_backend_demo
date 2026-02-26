from django.db import models
from django.contrib.postgres.fields import ArrayField
from data.whouse.models import Whouse
from apps.common.models import BaseModel

class ProductType(BaseModel):
    name = models.CharField(max_length=255)
    types = ArrayField(base_field=models.CharField(max_length=255)) 
    unities = ArrayField(base_field=models.CharField(max_length=255))
    whouse = models.ForeignKey(Whouse, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
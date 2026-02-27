from django.db import models
from apps.common.models import BaseModel

# Create your models here.
class Whouse(BaseModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
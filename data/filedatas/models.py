from django.db import models
from apps.common.models import BaseModel
from data.users.models import FactoryUser

# Create your models here.
class File(BaseModel):
    TYPE_CHOICES = (
        ('DRIVER', 'Driver'),
        ('TRANSPORT', 'Transport'),
        ('SUPPLIER', 'Supplier'),
        ('CLIENT', 'Client'),
        ('SUBORDER', 'Suborder'),
        ("PRODUCT", "Product"),
        ("OTHER", "Other"),
    )

    file = models.FileField(upload_to='files/')


class Documents(BaseModel):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default='OTHER')
    object_id = models.UUIDField(null=True, blank=True)
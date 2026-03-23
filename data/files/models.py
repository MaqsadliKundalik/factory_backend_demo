from django.db import models
from apps.common.models import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.files.models import File
# Create your models here.
class File(BaseModel):

    file = models.FileField(upload_to='files/')


class Documents(BaseModel):
    TYPE_CHOICES = (
        ('DRIVER', 'Driver'),
        ('TRANSPORT', 'Transport'),
        ('SUPPLIER', 'Supplier'),
        ('CLIENT', 'Client'),
        ('SUBORDER', 'Suborder'),
        ("PRODUCT", "Product"),
        ("OTHER", "Other"),
    )

    file: 'File' = models.ForeignKey("files.File", on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES, default='OTHER')
    object_id = models.UUIDField(null=True, blank=True)
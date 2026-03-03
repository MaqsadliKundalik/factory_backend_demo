from django.db import models
from django.conf import settings
from apps.common.models import BaseModel

# Create your models here.
class File(BaseModel):
    file = models.FileField(upload_to='files/')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

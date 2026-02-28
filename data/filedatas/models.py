from django.db import models
from django.contrib.auth.models import User
from apps.common.models import BaseModel

# Create your models here.
class File(BaseModel):
    file = models.FileField(upload_to='files/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

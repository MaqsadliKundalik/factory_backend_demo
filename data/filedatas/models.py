from django.db import models
from apps.common.models import BaseModel
from data.users.models import FactoryUser

# Create your models here.
class File(BaseModel):
    file = models.FileField(upload_to='files/')

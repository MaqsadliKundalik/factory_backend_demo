from django.db import models
from apps.common.models import BaseModel


# Create your models here.
class Notification(BaseModel):
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    from_role = models.CharField(max_length=255)
    to_role = models.CharField(max_length=255)
    
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title
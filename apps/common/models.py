from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from uuid import uuid4 as _uuid4


def uuid7():

    return _uuid4()

# Create your models here.
class BaseModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def update(self, **kwargs):

        for key, value in kwargs.items():

            setattr(self, key, value)

        self.save()

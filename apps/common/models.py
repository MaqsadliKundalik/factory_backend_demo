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

class UserPermissions(BaseModel):
    # Link to any Actor (Manager, Operator, Driver, Guard)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id is CharField to support both UUID and Integer IDs from different models
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey("content_type", "object_id")
    
    crud_whouse = models.BooleanField(default=False)
    crud_whouse_manager = models.BooleanField(default=False)
    crud_factory_operator = models.BooleanField(default=False)
    crud_driver = models.BooleanField(default=False)
    crud_guard = models.BooleanField(default=False)
    crud_product_type = models.BooleanField(default=False)
    crud_transport = models.BooleanField(default=False)

    read_whouse = models.BooleanField(default=False)
    read_whouse_manager = models.BooleanField(default=False)
    read_factory_operator = models.BooleanField(default=False)
    read_driver = models.BooleanField(default=False)
    read_guard = models.BooleanField(default=False)
    read_product_type = models.BooleanField(default=False)
    read_transport = models.BooleanField(default=False)

    
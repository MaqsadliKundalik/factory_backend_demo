from django.db import models
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    crud_whouse = models.BooleanField(default=False)
    crud_whouse_manager = models.BooleanField(default=False)
    crud_factory_operator = models.BooleanField(default=False)
    crud_driver = models.BooleanField(default=False)
    crud_guard = models.BooleanField(default=False)

    read_whouse = models.BooleanField(default=False)
    read_whouse_manager = models.BooleanField(default=False)
    read_factory_operator = models.BooleanField(default=False)
    read_driver = models.BooleanField(default=False)
    read_guard = models.BooleanField(default=False)

    
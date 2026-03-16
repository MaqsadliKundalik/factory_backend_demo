from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from uuid import uuid4 as _uuid4


def uuid7():

    return _uuid4()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


# Create your models here.
class BaseModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()
    del_objects = DeletedManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    def update(self, **kwargs):

        for key, value in kwargs.items():

            setattr(self, key, value)

        self.save()

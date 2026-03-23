from django.core.exceptions import ValidationError
from django.db import models
from apps.common.models import BaseModel
from data.files.models import File


class Supplier(BaseModel):
    class Type(models.TextChoices):
        INTERNAL = 'INTERNAL', 'Internal'
        EXTERNAL = 'EXTERNAL', 'External'

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.INTERNAL)
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=9, null=True, blank=True)
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)

    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        if self.type == self.Type.INTERNAL:
            errors = {}
            if not self.inn_number:
                errors['inn_number'] = 'Internal supplier uchun inn_number majburiy.'
            if not self.whouse_id:
                errors['whouse'] = 'Internal supplier uchun whouse majburiy.'
            if errors:
                raise ValidationError(errors)

    list_display = ["name", "inn_number", "whouse", "files"]

    orders: "models.QuerySet[Order]" 

    def __str__(self):
        return self.name


class SupplierPhone(BaseModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="phones")
    phone_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    list_display = ["supplier", "phone_number", "name", "role"]
    
    def __str__(self):
        return f"{self.phone_number} - {self.name} - {self.role}"

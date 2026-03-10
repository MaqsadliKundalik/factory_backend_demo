from django.db import models
from apps.common.models import BaseModel
from data.filedatas.models import File


class Supplier(BaseModel):
    name = models.CharField(max_length=255)
    inn_number = models.CharField(max_length=9)
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    whouse = models.ForeignKey('factory_whouse.Whouse', on_delete=models.CASCADE)
    files: "models.QuerySet[File]" = models.ManyToManyField('filedatas.File', related_name='suppliers', null=True, blank=True)

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


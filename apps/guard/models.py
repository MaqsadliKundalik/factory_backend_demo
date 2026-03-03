from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.hashers import make_password, check_password

from apps.common.models import BaseModel
# Create your models here.

class Guard(BaseModel):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25)
    password = models.CharField(max_length=128)
    
    whouses = models.ManyToManyField("factory_whouse.Whouse", related_name='guards')


    list_display = ["name", "phone_number", "password", "whouse"]


    @property
    def is_authenticated(self):
        return True


    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name
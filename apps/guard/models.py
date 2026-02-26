from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from apps.common.models import BaseModel
# Create your models here.

class Guard(BaseModel):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25)
    password = models.CharField(max_length=128)
    
    whouse = models.ForeignKey("factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True)

    @property
    def is_authenticated(self):
        return True

    def new_session(self):
        from apps.session.models import GuardSession
        return GuardSession.for_guard(self)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name
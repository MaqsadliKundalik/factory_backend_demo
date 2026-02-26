from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.hashers import make_password, check_password

from apps.common.models import BaseModel, UserPermissions
# Create your models here.

class Driver(BaseModel):
    CAR_TYPES = (
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('car', 'Car'),
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25)
    password = models.CharField(max_length=128)
    car_type = models.CharField(max_length=10, choices=CAR_TYPES)
    car_number = models.CharField(max_length=15)

    whouse = models.ForeignKey("factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True)

    # Dynamic Permissions
    permissions = GenericRelation(UserPermissions)

    def has_perm(self, perm_name):
        # By default drivers might not need complex granular permissions, 
        # but let's keep it consistent
        perm_obj = self.permissions.first()
        if not perm_obj:
            return False
        return getattr(perm_obj, perm_name, False)

    @property
    def is_authenticated(self):
        return True

    def new_session(self):
        from apps.session.models import DriverSession
        return DriverSession.for_driver(self)


    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name
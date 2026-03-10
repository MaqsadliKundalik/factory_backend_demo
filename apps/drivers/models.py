from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from apps.common.models import BaseModel
from data.filedatas.models import File


class Driver(BaseModel):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=128)
    # fcm_token = models.CharField(max_length=255, blank=True, null=True, help_text="Firebase Cloud Messaging token")
    
    photo = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)
    files = models.ManyToManyField(File, related_name='drivers', blank=True)

    whouse = models.ForeignKey("factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True)

    # Permission fields for compatibility with HasDynamicPermission
    MAIN_PAGE = models.BooleanField(default=False)
    PRODUCTS_PAGE = models.BooleanField(default=False)
    ORDERS_PAGE = models.BooleanField(default=False)
    TRANSPORTS_PAGE = models.BooleanField(default=False)
    WHEREHOUSES_PAGE = models.BooleanField(default=False)
    CLIENTS_PAGE = models.BooleanField(default=False)
    USERS_PAGE = models.BooleanField(default=False)
    READY_PRODUCTS_PAGE = models.BooleanField(default=False)
    DRIVERS_PAGE = models.BooleanField(default=False)

    @property
    def whouses(self):
        # Returns a queryset for compatibility with FactoryUser.whouses.all()
        from data.whouse.models import Whouse
        if self.whouse:
            return Whouse.objects.filter(id=self.whouse.id)
        return Whouse.objects.none()

    # Simple permissions for drivers
    def has_perm(self, perm_name):
        return False # Drivers usually don't have granular web permissions

    @property
    def is_authenticated(self):
        return True

    def new_session(self):
        from apps.session.models import DriverSession
        return DriverSession.for_driver(self)


    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name
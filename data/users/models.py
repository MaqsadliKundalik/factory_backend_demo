from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from typing import TYPE_CHECKING
from apps.common.models import BaseModel

if TYPE_CHECKING:
    from data.filedatas.models import File

# Create your managers here.
class FactoryUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Поле номера телефона обязательно для заполнения')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

# Create your models here.
class FactoryUser(BaseModel, AbstractBaseUser):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100, unique=True)
    # password field is provided by AbstractBaseUser
    
    role = models.CharField(max_length=50) # manager, operator, guard
    photo : 'File' = models.ForeignKey("filedatas.File", on_delete=models.SET_NULL, null=True, blank=True)

    MAIN_PAGE = models.BooleanField(default=False)
    PRODUCTS_PAGE = models.BooleanField(default=False)
    ORDERS_PAGE = models.BooleanField(default=False)
    TRANSPORTS_PAGE = models.BooleanField(default=False)
    WHEREHOUSES_PAGE = models.BooleanField(default=False)
    CLIENTS_PAGE = models.BooleanField(default=False)
    USERS_PAGE = models.BooleanField(default=False)
    READY_PRODUCTS_PAGE = models.BooleanField(default=False)
    DRIVERS_PAGE = models.BooleanField(default=False)
    SUPPLIERS_PAGE = models.BooleanField(default=False)

    whouses = models.ManyToManyField('factory_whouse.Whouse', blank=True, related_name='users')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = FactoryUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def has_perm(self, perm, obj=None):
        return self.is_staff or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_staff or self.is_superuser

    def new_session(self):
        from apps.session.models import FactoryUserSession
        return FactoryUserSession.for_factory_user(self)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

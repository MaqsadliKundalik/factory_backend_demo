from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password

# Create your managers here.
class FactoryUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

# Create your models here.
class FactoryUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100, unique=True)
    # password field is provided by AbstractBaseUser
    
    role = models.CharField(max_length=50) # manager, operator, guard
    
    MAIN_PAGE = models.BooleanField(default=False)
    PRODUCTS_PAGE = models.BooleanField(default=False)
    ORDERS_PAGE = models.BooleanField(default=False)
    TRANSPORTS_PAGE = models.BooleanField(default=False)
    CLIENTS_PAGE = models.BooleanField(default=False)
    USERS_PAGE = models.BooleanField(default=False)
    SETTINGS_PAGE = models.BooleanField(default=False)
    
    whouses = models.ManyToManyField('factory_whouse.Whouse', blank=True, related_name='users')
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = FactoryUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def has_perm(self, perm, obj=None):
        return getattr(self, perm, False) or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_staff or self.is_superuser

    def new_session(self):
        from apps.session.models import FactoryUserSession
        return FactoryUserSession.for_factory_user(self)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

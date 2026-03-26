from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from apps.common.models import BaseModel
from data.session.models import DriverSession
from typing import TYPE_CHECKING
from data.whouse.models import Whouse

if TYPE_CHECKING:
    from data.files.models import File


class Driver(BaseModel):

    class Type(models.TextChoices):
        INTERNAL = "INTERNAL", "Internal"
        EXTERNAL = "EXTERNAL", "External"

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    # fcm_token = models.CharField(max_length=255, blank=True, null=True, help_text="Firebase Cloud Messaging token")

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.INTERNAL)
    photo: "File" = models.ForeignKey(
        "files.File", on_delete=models.SET_NULL, null=True, blank=True
    )
    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )

    def clean(self):
        if self.type == self.Type.INTERNAL:
            errors = {}
            if not self.password:
                errors["password"] = "Internal driver uchun password majburiy."
            if not self.whouse_id:
                errors["whouse"] = "Internal driver uchun whouse majburiy."
            if errors:
                raise ValidationError(errors)

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
    SUPPLIERS_PAGE = models.BooleanField(default=False)
    EXCAVATORS_PAGE = models.BooleanField(default=False)

    @property
    def whouses(self):
        # Returns a queryset for compatibility with FactoryUser.whouses.all()
        if self.whouse:
            return Whouse.objects.filter(id=self.whouse.id)
        return Whouse.objects.none()

    # Simple permissions for drivers
    def has_perm(self, perm_name):
        return False  # Drivers usually don't have granular web permissions

    @property
    def is_authenticated(self):
        return True

    def new_session(self):
        return DriverSession.for_driver(self)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(
            ("pbkdf2_sha256$", "bcrypt$", "argon2$")
        ):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["phone_number", "whouse"]

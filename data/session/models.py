from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import admin
from django.conf import settings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.drivers.models import Driver
    from data.users.models import FactoryUser


# Create your models here.
class DriverSession(models.Model):
    driver: "Driver" = models.ForeignKey(
        "factory_drivers.Driver", on_delete=models.CASCADE, related_name="sessions"
    )
    fcm_token = models.CharField(max_length=512, null=True, blank=True)
    fcm_invalid = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)

    @classmethod
    def for_driver(cls, driver: "Driver"):

        new_session = cls.objects.create(driver=driver)

        return new_session

    @property
    def token(self):

        refresh = RefreshToken()
        refresh.payload["user_id"] = str(self.driver.id)
        refresh.payload["role"] = "driver"
        refresh.payload["session"] = str(self.id)

        return refresh

    class Admin(admin.ModelAdmin):
        list_display = ["driver"]

        list_filter = ["driver"]

        search_fields = ["driver__name"]

        date_hierarchy = "created_at"


class FactoryUserSession(models.Model):
    factory_user: "FactoryUser" = models.ForeignKey(
        "users.FactoryUser",
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,
        blank=True,
    )
    fcm_token = models.CharField(max_length=512, null=True, blank=True)
    fcm_invalid = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)

    @classmethod
    def for_factory_user(cls, factory_user):
        new_session = cls.objects.create(factory_user=factory_user)
        return new_session

    @property
    def token(self):
        refresh = RefreshToken()
        refresh.payload["user_id"] = str(self.factory_user.id)
        refresh.payload["role"] = getattr(self.factory_user, "role", "user")
        refresh.payload["session"] = str(self.id)
        return refresh

    class Admin(admin.ModelAdmin):
        list_display = ["factory_user"]
        list_filter = ["factory_user"]
        search_fields = ["factory_user__name"]
        date_hierarchy = "created_at"

class TgLocationSessions(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

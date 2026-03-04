from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import admin
from django.conf import settings

from apps.drivers.models import Driver

# Create your models here.
class DriverSession(models.Model):
    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="sessions"
    )

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
    factory_user = models.ForeignKey(
        "users.FactoryUser", on_delete=models.CASCADE, related_name="sessions",
        null=True, blank=True
    )

    @classmethod
    def for_factory_user(cls, factory_user):
        new_session = cls.objects.create(factory_user=factory_user)
        return new_session

    @property
    def token(self):
        refresh = RefreshToken()
        refresh.payload["user_id"] = str(self.factory_user.id)
        refresh.payload["role"] = getattr(self.factory_user, 'role', 'user')
        refresh.payload["session"] = str(self.id)
        return refresh

    class Admin(admin.ModelAdmin):
        list_display = ["factory_user"]
        list_filter = ["factory_user"]
        search_fields = ["factory_user__name"]
        date_hierarchy = "created_at"
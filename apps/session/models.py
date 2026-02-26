from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import admin
from apps.drivers.models import Driver
from apps.whouse_manager.models import WhouseManager

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

class WhouseManagerSession(models.Model):
    whouse_manager = models.ForeignKey(
        WhouseManager, on_delete=models.CASCADE, related_name="sessions"
    )

    @classmethod
    def for_whouse_manager(cls, whouse_manager: "WhouseManager"):

        new_session = cls.objects.create(whouse_manager=whouse_manager)

        return new_session

    @property
    def token(self):

        refresh = RefreshToken()
        refresh.payload["user_id"] = str(self.whouse_manager.id)
        refresh.payload["role"] = "manager"
        refresh.payload["session"] = str(self.id)

        return refresh

    class Admin(admin.ModelAdmin):
        list_display = ["whouse_manager"]

        list_filter = ["whouse_manager"]

        search_fields = ["whouse_manager__name"]

        date_hierarchy = "created_at"

class FactoryOperatorSession(models.Model):
    operator = models.ForeignKey(
        "factory_operator.FactoryOperator", on_delete=models.CASCADE, related_name="sessions"
    )

    @classmethod
    def for_operator(cls, operator):
        new_session = cls.objects.create(operator=operator)
        return new_session

    @property
    def token(self):
        refresh = RefreshToken()
        refresh.payload["user_id"] = str(self.operator.id)
        refresh.payload["role"] = "operator"
        refresh.payload["session"] = str(self.id)
        return refresh

    class Admin(admin.ModelAdmin):
        list_display = ["operator"]
        list_filter = ["operator"]
        search_fields = ["operator__name"]
        date_hierarchy = "created_at"

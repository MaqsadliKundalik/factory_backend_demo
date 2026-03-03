from django.contrib import admin
from apps.session.models import DriverSession, FactoryUserSession

# Register your models here.
admin.site.register(DriverSession)
admin.site.register(FactoryUserSession)

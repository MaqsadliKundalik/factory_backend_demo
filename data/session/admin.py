from django.contrib import admin
from data.session.models import DriverSession, FactoryUserSession

# Register your models here.
admin.site.register(DriverSession)
admin.site.register(FactoryUserSession)

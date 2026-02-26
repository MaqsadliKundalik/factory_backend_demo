from django.contrib import admin
from apps.session.models import DriverSession, WhouseManagerSession, FactoryOperatorSession, GuardSession

# Register your models here.
admin.site.register(DriverSession)
admin.site.register(WhouseManagerSession)
admin.site.register(FactoryOperatorSession)
admin.site.register(GuardSession)

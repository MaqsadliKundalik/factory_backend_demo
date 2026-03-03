from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "car_type", "car_number", "whouse"]

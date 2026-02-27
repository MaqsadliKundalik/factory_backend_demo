from django.contrib import admin
from .models import Client

# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn_number', 'phone_number', 'latitude', 'longitude', 'whouse']
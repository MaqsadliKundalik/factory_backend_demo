from django.contrib import admin
from .models import FactoryUser

@admin.register(FactoryUser)
class FactoryUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'role', 'whouse']
    list_filter = ['role', 'whouse']
    search_fields = ['name', 'phone_number']

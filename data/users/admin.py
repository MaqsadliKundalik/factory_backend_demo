from django.contrib import admin
from .models import FactoryUser

@admin.register(FactoryUser)
class FactoryUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'role', 'get_whouses']
    list_filter = ['role', 'whouses']
    search_fields = ['name', 'phone_number']

    def get_whouses(self, obj):
        return ", ".join([wh.name for wh in obj.whouses.all()])
    get_whouses.short_description = 'Warehouses'

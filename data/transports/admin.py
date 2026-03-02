from django.contrib import admin
from .models import Transport

# Register your models here.
@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'number', 'whouse']
    list_filter = ['whouse']
    search_fields = ['name', 'number']
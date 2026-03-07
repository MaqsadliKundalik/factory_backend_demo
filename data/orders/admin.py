from django.contrib import admin
from .models import Order, SubOrder

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'display_id', 'whouse', 'status', 'created_at']
    list_filter = ['status', 'whouse', 'created_at']
    search_fields = ['display_id', 'whouse__name']
    ordering = ['-created_at']

@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'driver', 'transport', 'status', 'created_at']
    list_filter = ['status', 'order', 'driver', 'transport', 'created_at']
    search_fields = ['order__display_id', 'driver__name', 'transport__model']
    ordering = ['-created_at']

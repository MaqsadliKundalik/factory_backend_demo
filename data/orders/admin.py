from django.contrib import admin
from .models import Order, SubOrder, OrderItem, SubOrderItem

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

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'created_at']
    list_filter = ['order', 'product', 'created_at']
    search_fields = ['order__display_id', 'product__name']
    ordering = ['-created_at']

@admin.register(SubOrderItem)
class SubOrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'sub_order', 'product', 'quantity', 'created_at']
    list_filter = ['sub_order', 'product', 'created_at']
    search_fields = ['sub_order__order__display_id', 'product__name']
    ordering = ['-created_at']

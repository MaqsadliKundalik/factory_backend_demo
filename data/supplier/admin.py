from django.contrib import admin
from .models import Supplier, SupplierPhone

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn_number')
    search_fields = ('name', 'inn_number')

@admin.register(SupplierPhone)
class SupplierPhoneAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'phone_number')
    search_fields = ('supplier__name', 'phone_number')


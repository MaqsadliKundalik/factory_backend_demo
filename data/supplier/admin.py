from django.contrib import admin
from .models import Supplier, SupplierPhone

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn_number', 'whouse')
    search_fields = ('name', 'inn_number')
    list_filter = ('whouse',)

@admin.register(SupplierPhone)
class SupplierPhoneAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'phone_number')
    search_fields = ('supplier__name', 'phone_number')
    list_filter = ('supplier',)


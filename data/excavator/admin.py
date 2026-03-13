from django.contrib import admin
from .models import ExcavatorOrder, ExcavatorSubOrder

@admin.register(ExcavatorOrder)
class ExcavatorOrderAdmin(admin.ModelAdmin):
    list_display = ['display_id', 'client_name', 'phone_number', 'start_date', 'end_date', 'status', 'payment_status']
    list_filter = ['status', 'payment_status']
    search_fields = ['client_name', 'phone_number']

@admin.register(ExcavatorSubOrder)
class ExcavatorSubOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'status']
    list_filter = ['status']
    search_fields = ['parent__client_name']
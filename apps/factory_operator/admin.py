from apps.common.admin import UserPermissionsInline
from django.contrib import admin
from .models import FactoryOperator

@admin.register(FactoryOperator)
class FactoryOperatorAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "whouse"]
    inlines = [UserPermissionsInline]

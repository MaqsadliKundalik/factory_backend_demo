from apps.common.admin import UserPermissionsInline
from django.contrib import admin
from .models import Guard

@admin.register(Guard)
class GuardAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "whouse"]
    inlines = [UserPermissionsInline]
from apps.common.admin import UserPermissionsInline
from django.contrib import admin
from .models import WhouseManager

@admin.register(WhouseManager)
class WhouseManagerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "whouse"]
    inlines = [UserPermissionsInline]

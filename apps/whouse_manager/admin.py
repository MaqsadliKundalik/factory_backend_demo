from apps.common.admin import UserPermissionsInline
from django.contrib import admin
from .models import WhouseManager

@admin.register(WhouseManager)
class WhouseManagerAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone_number", "get_whouses"]
    inlines = [UserPermissionsInline]

    def get_whouses(self, obj):
        return ", ".join([w.name for w in obj.whouses.all()])
    get_whouses.short_description = "Whouses"

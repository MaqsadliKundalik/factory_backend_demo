from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import UserPermissions

class UserPermissionsInline(GenericTabularInline):
    model = UserPermissions
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name = "User Permission"
    verbose_name_plural = "User Permissions"

@admin.register(UserPermissions)
class UserPermissionsAdmin(admin.ModelAdmin):
    list_display = ["content_object", "content_type", "object_id", "created_at"]
    list_filter = ["content_type"]
    search_fields = ["object_id"]

from django.contrib import admin
from .models import Notification

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "from_role", "to_role", "to_user_id", "title", "message", "is_read", "created_at"]
    list_filter = ["from_role", "to_role", "is_read", "created_at"]
    search_fields = ["title", "message"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
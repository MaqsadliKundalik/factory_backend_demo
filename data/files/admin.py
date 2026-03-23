from django.contrib import admin
from .models import File, Documents

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'created_at', 'updated_at')

@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'type', 'object_id', 'created_at', 'updated_at')

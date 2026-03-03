from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', "user", 'created_at', 'updated_at')

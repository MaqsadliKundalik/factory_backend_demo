from django.contrib import admin
from .models import FileData

@admin.register(FileData)
class FileDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', "user", 'created_at', 'updated_at')

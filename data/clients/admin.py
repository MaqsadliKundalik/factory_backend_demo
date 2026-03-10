from django.contrib import admin
from .models import Client, ClientPhone, ClientBranches

# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn_number', 'whouse']

@admin.register(ClientPhone)
class ClientPhoneAdmin(admin.ModelAdmin):
    list_display = ['client', 'phone_number', 'name', 'role']

@admin.register(ClientBranches)
class ClientBranchesAdmin(admin.ModelAdmin):
    list_display = ['client', 'name', 'address', 'longitude', 'latitude']
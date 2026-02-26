from django.contrib import admin
from .models import ProductType

# Register your models here.
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'whouse')
    search_fields = ('name', 'whouse__name')
    list_filter = ('whouse',)
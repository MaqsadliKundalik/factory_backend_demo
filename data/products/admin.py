from django.contrib import admin
from .models import ProductType, ProductUnit, Product, WhouseProducts

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'whouse')
    search_fields = ('name', 'whouse__name')
    list_filter = ('whouse',)

@admin.register(ProductUnit)
class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'whouse')
    search_fields = ('name', 'whouse__name')
    list_filter = ('whouse',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'whouse')
    search_fields = ('name', 'whouse__name')
    list_filter = ('whouse',)
    filter_horizontal = ('types',)

@admin.register(WhouseProducts)
class WhouseProductsAdmin(admin.ModelAdmin):
    list_display = ('product', 'whouse', 'quantity', 'status')
    list_filter = ('whouse', 'status')
    search_fields = ('product__name', 'whouse__name')

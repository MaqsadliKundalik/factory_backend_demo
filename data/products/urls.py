from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductTypeViewSet, ProductUnitViewSet, ProductViewSet, WhouseProductsViewSet

router = DefaultRouter()
router.register('types', ProductTypeViewSet, basename='product-type')
router.register('units', ProductUnitViewSet, basename='product-unit')
router.register('', ProductViewSet, basename='product')
router.register('whouse/', WhouseProductsViewSet, basename='whouse-products')

urlpatterns = [
    path('', include(router.urls)),
]
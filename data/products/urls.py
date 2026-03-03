
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ProductTypeViewSet, ProductUnitViewSet, ProductViewSet, 
    WhouseProductsViewSet, WhouseProductsHistoryViewSet, 
    WhouseProductsActionViewSet, ProductItemViewSet
)

router = DefaultRouter()
router.register('types', ProductTypeViewSet, basename='product-type')
router.register('units', ProductUnitViewSet, basename='product-unit')
router.register("history", WhouseProductsHistoryViewSet, basename='whouse-products-history')
router.register('whouse', WhouseProductsViewSet, basename='whouse-products')
router.register('actions', WhouseProductsActionViewSet, basename='whouse-products-actions')
router.register('items', ProductItemViewSet, basename='product-item')
router.register('', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
]
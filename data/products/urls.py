from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductTypeViewSet, ProductUnitViewSet, ProductViewSet

router = DefaultRouter()
router.register('types', ProductTypeViewSet, basename='product-type')
router.register('units', ProductUnitViewSet, basename='product-unit')
router.register('', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
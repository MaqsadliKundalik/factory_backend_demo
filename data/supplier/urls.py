from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import SupplierSelectView, SupplierViewSet, SupplierAndPhoneCreateView

router = DefaultRouter()
router.register('select', SupplierSelectView, basename='supplier-select')
router.register('create', SupplierAndPhoneCreateView, basename='supplier-create')
router.register('', SupplierViewSet, basename='supplier')

urlpatterns = router.urls

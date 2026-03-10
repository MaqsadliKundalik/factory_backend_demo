from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import SupplierViewSet, SupplierAndPhoneCreateView, SupplierSelectView

router = DefaultRouter()
router.register('', SupplierViewSet, basename='supplier')

urlpatterns = [
    path('create/', SupplierAndPhoneCreateView.as_view()),
    path('select/', SupplierSelectView.as_view()),
] + router.urls

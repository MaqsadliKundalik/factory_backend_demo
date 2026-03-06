from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import OrderViewSet, SubOrderViewSet, OrderAndSubOrderCreateView

router = DefaultRouter()
router.register('sub-orders', SubOrderViewSet, basename='suborder')
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    path('create-order-and-suborder/', OrderAndSubOrderCreateView.as_view(), name='order-and-suborder-create'),
] + router.urls

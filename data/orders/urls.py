from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, SubOrderViewSet

router = DefaultRouter()
router.register('', OrderViewSet, basename='order')
router.register('sub-orders', SubOrderViewSet, basename='suborder')

urlpatterns = router.urls

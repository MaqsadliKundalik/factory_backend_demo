from rest_framework.routers import DefaultRouter
from .views import ExcavatorOrderViewSet, ExcavatorSubOrderViewSet

router = DefaultRouter()
router.register('sub-orders', ExcavatorSubOrderViewSet, basename='excavator-suborder')
router.register('', ExcavatorOrderViewSet, basename='excavator-order')

urlpatterns = router.urls

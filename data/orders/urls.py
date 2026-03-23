from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, SubOrderViewSet

router = DefaultRouter()
router.register("sub-orders", SubOrderViewSet, basename="suborder")
router.register("", OrderViewSet, basename="order")

urlpatterns = router.urls

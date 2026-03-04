from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientBranchesViewSet

router = DefaultRouter()
router.register(r'', ClientViewSet)
router.register(r'branches', ClientBranchesViewSet)

urlpatterns = router.urls
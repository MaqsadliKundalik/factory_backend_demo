from rest_framework.routers import SimpleRouter
from .views import UnifiedUserViewSet

router = SimpleRouter()
router.register('', UnifiedUserViewSet, basename='unified-user')

urlpatterns = router.urls

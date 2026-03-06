from rest_framework.routers import SimpleRouter
from .views import FactoryUserResetPasswordViewSet, FactoryUserViewSet

router = SimpleRouter()
router.register('reset-password', FactoryUserResetPasswordViewSet, basename='factory-user-reset-password')
router.register('', FactoryUserViewSet, basename='factory-user')

urlpatterns = router.urls

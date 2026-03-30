from rest_framework.routers import SimpleRouter
from .views import FactoryUserResetPasswordViewSet, FactoryUserViewSet, UserSelectView

router = SimpleRouter()
router.register(
    "reset-password",
    FactoryUserResetPasswordViewSet,
    basename="factory-user-reset-password",
)
router.register("", FactoryUserViewSet, basename="factory-user")
router.register("select", UserSelectView, basename="factory-user-select")

urlpatterns = router.urls

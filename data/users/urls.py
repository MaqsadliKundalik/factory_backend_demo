from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import FactoryUserResetPasswordViewSet, FactoryUserViewSet, UserSelectView

router = SimpleRouter()
router.register(
    "reset-password",
    FactoryUserResetPasswordViewSet,
    basename="factory-user-reset-password",
)
router.register("", FactoryUserViewSet, basename="factory-user")

urlpatterns = [
    path("select/", UserSelectView.as_view(), name="factory-user-select"),
] + router.urls

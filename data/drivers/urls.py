from django.urls import path
from rest_framework.routers import DefaultRouter
from data.drivers.views import DriverViewSet, DriverPasswordChangeView, DriverSelectView

router = DefaultRouter()
router.register("", DriverViewSet, basename="driver")

urlpatterns = [
    path(
        "<uuid:driver_id>/change-password/",
        DriverPasswordChangeView.as_view(),
        name="driver-change-password",
    ),
    path("select/", DriverSelectView.as_view(), name="driver-select"),
] + router.urls

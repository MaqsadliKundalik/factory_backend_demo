from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserPermissionsViewSet

router = DefaultRouter()
router.register(r"user-permissions", UserPermissionsViewSet, basename="user-permissions")

urlpatterns = [
    path("", include(router.urls)),
]

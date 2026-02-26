from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.whouse.views import WhouseViewSet

router = DefaultRouter()
router.register(r'', WhouseViewSet, basename='whouse')

urlpatterns = [
    path("", include(router.urls)),
]
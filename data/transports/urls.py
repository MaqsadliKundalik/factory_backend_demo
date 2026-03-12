from rest_framework.routers import DefaultRouter
from .views import TransportViewSet, TransportSelectView
from django.urls import path

router = DefaultRouter()
router.register('', TransportViewSet, basename='transport')

urlpatterns = [
    path('select/', TransportSelectView.as_view(), name='transport-select'),
] + router.urls
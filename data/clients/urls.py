from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientBranchesViewSet, ClientAndBranchesCreateView

router = DefaultRouter()
router.register(r'', ClientViewSet)
router.register(r'branches', ClientBranchesViewSet)

urlpatterns = [
    path('create/', ClientAndBranchesCreateView.as_view(), name='client-create'),
] + router.urls

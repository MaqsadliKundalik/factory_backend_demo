from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientBranchesViewSet, ClientAndBranchesCreateView

router = DefaultRouter()
router.register(r'branches', ClientBranchesViewSet)
router.register(r'', ClientViewSet)

urlpatterns = [
    path('create/', ClientAndBranchesCreateView.as_view(), name='client-create'),
] + router.urls

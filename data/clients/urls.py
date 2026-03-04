from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientBranchesViewSet, ClientAndBranchesCreateUpdateView

router = DefaultRouter()
router.register(r'', ClientViewSet)

urlpatterns = [
    path('create-update/', ClientAndBranchesCreateUpdateView.as_view(), name='client-create-update'),
] + router.urls

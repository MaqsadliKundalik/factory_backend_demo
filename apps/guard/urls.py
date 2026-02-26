from django.urls import path
from .views import GuardListCreateAPIView, GuardRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", GuardListCreateAPIView.as_view(), name="guard_list_create"),
    path("<int:pk>/", GuardRetrieveUpdateDestroyAPIView.as_view(), name="guard_detail"),
]

from django.urls import path
from apps.drivers.views import DriverListCreateAPIView, DriverRetrieveUpdateDestroyAPIView, DriverPasswordChangeView

urlpatterns = [
    path("<int:driver_id>/change-password/", DriverPasswordChangeView.as_view(), name="driver-change-password"),
    path("<int:pk>/", DriverRetrieveUpdateDestroyAPIView.as_view()),
    path("", DriverListCreateAPIView.as_view()),
]
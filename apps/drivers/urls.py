from django.urls import path
from apps.drivers.views import DriverListCreateAPIView, DriverRetrieveUpdateDestroyAPIView, DriverPasswordChangeView

urlpatterns = [
    path("<uuid:driver_id>/change-password/", DriverPasswordChangeView.as_view(), name="driver-change-password"),
    path("<uuid:pk>/", DriverRetrieveUpdateDestroyAPIView.as_view()),
    path("", DriverListCreateAPIView.as_view()),
]
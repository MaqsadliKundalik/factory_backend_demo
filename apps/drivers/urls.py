from django.urls import path
from apps.drivers.views import DriverListCreateAPIView, DriverRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", DriverListCreateAPIView.as_view()),
    path("<int:pk>/", DriverRetrieveUpdateDestroyAPIView.as_view()),
]
from django.urls import path
from .views import WhouseManagerListCreateAPIView, WhouseManagerRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", WhouseManagerListCreateAPIView.as_view()),
    path("<int:pk>/", WhouseManagerRetrieveUpdateDestroyAPIView.as_view()),
]
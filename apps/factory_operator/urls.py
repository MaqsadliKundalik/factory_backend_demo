from django.urls import path
from apps.factory_operator.views import FactoryOperatorListCreateAPIView, FactoryOperatorRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", FactoryOperatorListCreateAPIView.as_view()),
    path("<int:pk>/", FactoryOperatorRetrieveUpdateDestroyAPIView.as_view()),
]
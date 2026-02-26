from django.urls import path
from .views import ProductTypeListCreateAPIView, ProductTypeRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('types/', ProductTypeListCreateAPIView.as_view(), name='product-type-list-create'),
    path('types/<int:pk>/', ProductTypeRetrieveUpdateDestroyAPIView.as_view(), name='product-type-retrieve-update-destroy'),
]
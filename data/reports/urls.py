from django.urls import path
from .views import (
    YukXatiExcelView,
    IshonchQogoziExcelView,
    BuyurtmalarHisobotiExcelView,
    YetkazibBeruvchilarHisobotiExcelView,
)

urlpatterns = [
    path('waybill/<uuid:pk>/', YukXatiExcelView.as_view(), name='waybill-excel'),
    path('proxy/<uuid:pk>/', IshonchQogoziExcelView.as_view(), name='proxy-excel'),
    path('orders-report/', BuyurtmalarHisobotiExcelView.as_view(), name='orders-report-excel'),
    path('suppliers-report/', YetkazibBeruvchilarHisobotiExcelView.as_view(), name='suppliers-report-excel'),
]

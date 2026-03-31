from django.urls import path
from .views import (
    YukXatiExcelView,
    IshonchQogoziExcelView,
    BuyurtmalarHisobotiExcelView,
    YetkazibBeruvchilarHisobotiExcelView,
    ExcavatorHisobotiExcelView,
)

urlpatterns = [
    path(' /<uuid:pk>/', YukXatiExcelView.as_view(), name='waybill-excel'),
    path('proxy/<uuid:pk>/', IshonchQogoziExcelView.as_view(), name='proxy-excel'),
    path('orders-report/', BuyurtmalarHisobotiExcelView.as_view(), name='orders-report-excel'),
    path('suppliers-r eport/', YetkazibBeruvchilarHisobotiExcelView.as_view(), name='suppliers-report-excel'),
    path('excavator-report/', ExcavatorHisobotiExcelView.as_view(), name='excavator-report-excel'),
]

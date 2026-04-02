from django.urls import path
from .views import (
    YukXatiExcelView,
    IshonchQogoziExcelView,
    BuyurtmalarHisobotiExcelView,
    YetkazibBeruvchilarHisobotiExcelView,
    ExcavatorHisobotiExcelView,
    KalkulyatsiyaHisobotiExcelView,
)

urlpatterns = [
    path('waybill/<uuid:pk>/', YukXatiExcelView.as_view(), name='waybill-excel'),
    path('suppliers-report/', YetkazibBeruvchilarHisobotiExcelView.as_view(), name='suppliers-report-excel'),
    path('proxy/<uuid:pk>/', IshonchQogoziExcelView.as_view(), name='proxy-excel'),
    path('orders-report/', BuyurtmalarHisobotiExcelView.as_view(), name='orders-report-excel'),
    path('excavator-report/', ExcavatorHisobotiExcelView.as_view(), name='excavator-report-excel'),
    path('kalkulyatsiya-report/', KalkulyatsiyaHisobotiExcelView.as_view(), name='kalkulyatsiya-report-excel'),
]

from django.urls import path
from .views import (
    YukXatiExcelView,
    IshonchQogoziExcelView,
    BuyurtmalarHisobotiExcelView,
    YetkazibBeruvchilarHisobotiExcelView,
)

urlpatterns = [
    path('yuk-xati/<int:display_id>/', YukXatiExcelView.as_view(), name='yuk-xati-excel'),
    path('ishonch-qogozi/<int:display_id>/', IshonchQogoziExcelView.as_view(), name='ishonch-qogozi-excel'),
    path('buyurtmalar-hisoboti/', BuyurtmalarHisobotiExcelView.as_view(), name='buyurtmalar-hisoboti-excel'),
    path('yetkazib-beruvchilar-hisoboti/', YetkazibBeruvchilarHisobotiExcelView.as_view(), name='yetkazib-beruvchilar-hisoboti-excel'),
]

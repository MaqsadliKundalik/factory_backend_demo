from django.urls import path
from .views import CountStatsView, IncomeProductStatsView, SupplierIncomeProductStatsView

urlpatterns = [
    path('', CountStatsView.as_view(), name='count-stats'),
    path('income-product/', IncomeProductStatsView.as_view(), name='income-product-stats'),
    path('supplier-income-product/', SupplierIncomeProductStatsView.as_view(), name='supplier-income-product-stats'),
]
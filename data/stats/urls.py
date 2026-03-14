from django.urls import path
from .views import CountStatsView, IncomeProductStatsView, SupplierIncomeProductStatsView

urlpatterns = [
    path('<uuid:whouse_id>/', CountStatsView.as_view(), name='count-stats'),
    path('income-product/<uuid:whouse_id>/', IncomeProductStatsView.as_view(), name='income-product-stats'),
    path('supplier-income-product/<uuid:whouse_id>/', SupplierIncomeProductStatsView.as_view(), name='supplier-income-product-stats'),
]
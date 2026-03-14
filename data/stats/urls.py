from django.urls import path
from .views import (
    CountStatsView, 
    IncomeProductStatsView, 
    SupplierIncomeProductStatsView,
    OutcomingProductStatsView
)

urlpatterns = [
    path('<uuid:whouse_id>/', CountStatsView.as_view(), name='count-stats'),
    path('income-products/<uuid:whouse_id>/', IncomeProductStatsView.as_view(), name='income-product-stats'),
    path('supplier-income-products/<uuid:whouse_id>/', SupplierIncomeProductStatsView.as_view(), name='supplier-income-product-stats'),
    path('outcome-products/<uuid:whouse_id>/', OutcomingProductStatsView.as_view(), name='outcome-product-stats'),
]

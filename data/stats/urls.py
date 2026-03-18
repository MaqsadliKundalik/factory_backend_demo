from django.urls import path
from .views import (
    CountStatsView,
    IncomeProductStatsView,
    SupplierIncomeProductStatsView,
    OutcomingProductStatsView,
    OrderStatusStatsView,
    OrderStatusDurationStatsView,
    ExcavatorOrderStatusStatsView,
    ExcavatorStatusDurationStatsView,
)

urlpatterns = [
    path('', CountStatsView.as_view(), name='count-stats'),
    path('income-products/', IncomeProductStatsView.as_view(), name='income-product-stats'),
    path('supplier-income-products/', SupplierIncomeProductStatsView.as_view(), name='supplier-income-product-stats'),
    path('outcome-products/', OutcomingProductStatsView.as_view(), name='outcome-product-stats'),
    path('orders/', OrderStatusStatsView.as_view(), name='orders-stats'),
    path('orders/status/', OrderStatusDurationStatsView.as_view(), name='orders-status-duration-stats'),
    path('excavator/orders/', ExcavatorOrderStatusStatsView.as_view(), name='excavator-orders-stats'),
    path('excavator/orders/status/', ExcavatorStatusDurationStatsView.as_view(), name='excavator-orders-status-duration-stats'),
]

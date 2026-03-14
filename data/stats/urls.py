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
    path('<uuid:whouse_id>/', CountStatsView.as_view(), name='count-stats'),
    path('income-products/<uuid:whouse_id>/', IncomeProductStatsView.as_view(), name='income-product-stats'),
    path('supplier-income-products/<uuid:whouse_id>/', SupplierIncomeProductStatsView.as_view(), name='supplier-income-product-stats'),
    path('outcome-products/<uuid:whouse_id>/', OutcomingProductStatsView.as_view(), name='outcome-product-stats'),
    path('orders/<uuid:whouse_id>/', OrderStatusStatsView.as_view(), name='orders-stats'),
    path('orders/status/<uuid:whouse_id>/', OrderStatusDurationStatsView.as_view(), name='orders-status-duration-stats'),
    path('excavator/orders/', ExcavatorOrderStatusStatsView.as_view(), name='excavator-orders-stats'),
    path('excavator/orders/status/', ExcavatorStatusDurationStatsView.as_view(), name='excavator-orders-status-duration-stats'),
]

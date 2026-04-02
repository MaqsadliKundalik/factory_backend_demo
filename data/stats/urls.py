from django.urls import path
from .views import (
    CountStatsView,
    IncomeProductStatsView,
    OutcomingProductStatsView,
    WhouseProductsStatsView,
    OrderStatusStatsView,
    ExcavatorOrderStatusStatsView,
)

urlpatterns = [
    path('', CountStatsView.as_view(), name='count-stats'),
    path('income-products/', IncomeProductStatsView.as_view(), name='income-product-stats'),
    path('outcome-products/', OutcomingProductStatsView.as_view(), name='outcome-product-stats'),
    path('whouse-products/', WhouseProductsStatsView.as_view(), name='whouse-products-stats'),
    path('orders/', OrderStatusStatsView.as_view(), name='orders-stats'),
    path('excavator/orders/', ExcavatorOrderStatusStatsView.as_view(), name='excavator-orders-stats'),
]

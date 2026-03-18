from datetime import date as date_type, datetime
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from data.stats.serializers import (
    SimpleCountStatsSerializer,
    IncomeProductStatsSerializer,
    SupplierIncomeProductStatsSerializer,
    OutcomingProductStatsSerializer,
    OrderStatusStatsSerializer,
    StatusDurationSerializer,
    ExcavatorOrderStatusStatsSerializer,
    ExcavatorStatusDurationSerializer,
)
from data.products.models import Product, WhouseProducts, WhouseProductsHistory, HistoryStatus
from data.supplier.models import Supplier
from apps.drivers.models import Driver
from data.clients.models import Client
from data.transports.models import Transport
from data.orders.models import Order, SubOrder
from data.excavator.models import ExcavatorOrder, ExcavatorSubOrder
from rest_framework.response import Response
from django.db.models import Sum
from data.whouse.models import Whouse

WHOUSE_PARAM = openapi.Parameter(
    'whouse',
    openapi.IN_QUERY,
    description='Whouse ID (optional, filters by warehouse)',
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_UUID,
    required=False,
)
DATE_RANGE_PARAMS = [
    WHOUSE_PARAM,
    openapi.Parameter(
        'start_date',
        openapi.IN_QUERY,
        description='Filter from date (YYYY-MM-DD)',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        required=False,
    ),
    openapi.Parameter(
        'end_date',
        openapi.IN_QUERY,
        description='Filter to date (YYYY-MM-DD)',
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        required=False,
    ),
]
OUTCOMING_PRODUCT_FILTER_PARAMS = DATE_RANGE_PARAMS + [
    openapi.Parameter(
        'client',
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_UUID,
        description="Client ID",
    ),
]


def calculate_status_durations(sub_orders):
    duration_totals = {}
    duration_counts = {}
    for sub_order in sub_orders:
        history = sub_order.status_history or []
        for i, entry in enumerate(history):
            if not isinstance(entry, dict):
                continue
            status_key = entry.get('status', '').upper()
            if not status_key or i + 1 >= len(history):
                continue
            next_entry = history[i + 1]
            if not isinstance(next_entry, dict):
                continue
            try:
                t1 = datetime.fromisoformat(str(entry['timestamp']))
                t2 = datetime.fromisoformat(str(next_entry['timestamp']))
                minutes = (t2 - t1).total_seconds() / 60
                if minutes >= 0:
                    duration_totals[status_key] = duration_totals.get(status_key, 0) + minutes
                    duration_counts[status_key] = duration_counts.get(status_key, 0) + 1
            except (KeyError, ValueError):
                continue

    def avg(key):
        if duration_counts.get(key):
            return round(duration_totals[key] / duration_counts[key], 2)
        return 0.0

    return avg


class WhouseViewMixin(APIView):
    def get_whouse_filter(self, request):
        whouse_id = request.query_params.get('whouse')
        if not whouse_id:
            return {}
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return None
        return {'whouse': whouse}

    def whouse_not_found(self):
        return Response({'error': 'Whouse not found'}, status=404)


class DateRangeFilterMixin:
    def get_date_filters(self, request, prefix=''):
        filters = {}
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')
        field = f'{prefix}created_at__date'
        if start:
            try:
                filters[f'{field}__gte'] = date_type.fromisoformat(start)
            except ValueError:
                pass
        if end:
            try:
                filters[f'{field}__lte'] = date_type.fromisoformat(end)
            except ValueError:
                pass
        return filters


class OutcomingProductFilterMixin(DateRangeFilterMixin):
    def get_outcoming_product_filters(self, request, prefix=''):
        filters = self.get_date_filters(request, prefix)
        client = request.query_params.get('client')
        if client:
            filters[f'{prefix}client_id'] = client
        return filters


class CountStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_date_filters(request)
        return Response({
            'drivers': Driver.objects.filter(**whouse_filter, **df).count(),
            'suppliers': Supplier.objects.filter(**whouse_filter, **df).count(),
            'clients': Client.objects.filter(**whouse_filter, **df).count(),
            'transports': Transport.objects.filter(**whouse_filter, **df).count(),
            'products': WhouseProducts.objects.filter(**whouse_filter, **df).count(),
            'orders': Order.objects.filter(**whouse_filter, **df).count(),
        })


class IncomeProductStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_date_filters(request)
        products = Product.objects.filter(**whouse_filter, items__isnull=True)
        result = []
        for product in products:
            total_income = WhouseProductsHistory.objects.filter(product=product, status=HistoryStatus.IN, **whouse_filter, **df).aggregate(total=Sum('quantity'))['total'] or 0
            result.append({'product': product.name, 'income': total_income})
        serializer = IncomeProductStatsSerializer(result, many=True)
        return Response(serializer.data)


class OutcomingProductStatsView(OutcomingProductFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=OUTCOMING_PRODUCT_FILTER_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_outcoming_product_filters(request)
        products = Product.objects.filter(**whouse_filter)
        result = []
        for product in products:
            total_income = WhouseProductsHistory.objects.filter(product=product, status=HistoryStatus.OUT, **whouse_filter, **df).aggregate(total=Sum('quantity'))['total'] or 0
            result.append({'product': product.name, 'outcoming': total_income})
        serializer = OutcomingProductStatsSerializer(result, many=True)
        return Response(serializer.data)


class SupplierIncomeProductStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_date_filters(request)
        suppliers = Supplier.objects.filter(**whouse_filter)
        products = Product.objects.filter(**whouse_filter, items__isnull=True)
        result = []
        for supplier in suppliers:
            total = 0
            product_result = []
            for product in products:
                total_income = WhouseProductsHistory.objects.filter(product=product, supplier=supplier, status=HistoryStatus.IN, **whouse_filter, **df).aggregate(total=Sum('quantity'))['total'] or 0
                total += total_income
                product_result.append({'product': product.name, 'income': total_income})
            result.append({'supplier': supplier.name, 'total': total, 'products': product_result})
        serializer = SupplierIncomeProductStatsSerializer(result, many=True)
        return Response(serializer.data)


class OrderStatusStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_date_filters(request)
        qs = Order.objects.filter(**whouse_filter, **df)
        result = {
            'total': qs.count(),
            'new': qs.filter(status=Order.Status.NEW).count(),
            'in_progress': qs.filter(status=Order.Status.IN_PROGRESS).count(),
            'on_way': qs.filter(status=Order.Status.ON_WAY).count(),
            'arrived': qs.filter(status=Order.Status.ARRIVED).count(),
            'unloading': qs.filter(status=Order.Status.UNLOADING).count(),
            'completed': qs.filter(status=Order.Status.COMPLETED).count()
        }
        serializer = OrderStatusStatsSerializer(result)
        return Response(serializer.data)


class OrderStatusDurationStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        if whouse_filter:
            whouse_filter = {'order__whouse': whouse_filter['whouse']}
        df = self.get_date_filters(request, prefix='order__')
        sub_orders = SubOrder.objects.filter(**whouse_filter, **df).exclude(status_history=[])
        avg = calculate_status_durations(sub_orders)
        result = {
            'total': sub_orders.count(),
            'new': avg('NEW'),
            'in_progress': avg('IN_PROGRESS'),
            'on_way': avg('ON_WAY'),
            'arrived': avg('ARRIVED'),
            'unloading': avg('UNLOADING'),
            'completed': avg('COMPLETED')
        }
        serializer = StatusDurationSerializer(result)
        return Response(serializer.data)


class ExcavatorOrderStatusStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        df = self.get_date_filters(request)
        qs = ExcavatorOrder.objects.filter(**df)
        result = {
            'total': qs.count(),
            'new': qs.filter(status=ExcavatorOrder.Status.NEW).count(),
            'in_progress': qs.filter(status=ExcavatorOrder.Status.IN_PROGRESS).count(),
            'paused': qs.filter(status=ExcavatorOrder.Status.PAUSED).count(),
            'completed': qs.filter(status=ExcavatorOrder.Status.COMPLETED).count(),
            'expired': qs.filter(status=ExcavatorOrder.Status.EXPIRED).count()
        }
        serializer = ExcavatorOrderStatusStatsSerializer(result)
        return Response(serializer.data)


class ExcavatorStatusDurationStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        df = self.get_date_filters(request)
        sub_orders = ExcavatorSubOrder.objects.filter(**df).exclude(status_history=[])
        avg = calculate_status_durations(sub_orders)
        result = {
            'total': sub_orders.count(),
            'new': avg('NEW'),
            'in_progress': avg('IN_PROGRESS'),
            'paused': avg('PAUSED'), 
            'completed': avg('COMPLETED'),
            'expired': avg('EXPIRED')
        }
        serializer = ExcavatorStatusDurationSerializer(result)
        return Response(serializer.data)

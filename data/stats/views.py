from datetime import date as date_type, datetime
from decimal import Decimal
from django.utils import timezone
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from data.stats.serializers import (
    SimpleCountStatsSerializer,
    IncomeProductStatsSerializer,
    OutcomingProductStatsSerializer,
    ProductStatsSerializer,
    WhouseProductsStatsSerializer,
    SupplierIncomeProductStatsSerializer,
    OrderStatusStatsSerializer,
    StatusDurationSerializer,
    ExcavatorOrderStatusStatsSerializer,
    ExcavatorStatusDurationSerializer,
    OrderStatsSerializer,
    ExcavatorOrderStatsSerializer,
)
from data.products.models import (
    Product,
    WhouseProducts,
    WhouseProductsHistory,
    HistoryStatus,
)
from data.supplier.models import Supplier
from data.drivers.models import Driver
from data.clients.models import Client
from data.transports.models import Transport
from data.orders.models import Order, SubOrder, OrderItem
from data.excavator.models import ExcavatorOrder, ExcavatorSubOrder
from rest_framework.response import Response
from django.db.models import Sum
from data.whouse.models import Whouse

WHOUSE_PARAM = openapi.Parameter(
    "whouse",
    openapi.IN_QUERY,
    description="Whouse ID (optional, filters by warehouse)",
    type=openapi.TYPE_STRING,
    format=openapi.FORMAT_UUID,
    required=False,
)
DATE_RANGE_PARAMS = [
    WHOUSE_PARAM,
    openapi.Parameter(
        "start_date",
        openapi.IN_QUERY,
        description="Filter from date (YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        required=False,
    ),
    openapi.Parameter(
        "end_date",
        openapi.IN_QUERY,
        description="Filter to date (YYYY-MM-DD)",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_DATE,
        required=False,
    ),
]
OUTCOMING_PRODUCT_FILTER_PARAMS = DATE_RANGE_PARAMS + [
    openapi.Parameter(
        "client",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_UUID,
        description="Client ID",
    ),
]

INCOME_PRODUCT_FILTER_PARAMS = DATE_RANGE_PARAMS + [
    openapi.Parameter(
        "supplier",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_UUID,
        description="Supplier ID",
    ),
]


def _to_float(value):
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _build_income_product_stats(income_rows):
    product_map = {}

    for row in income_rows:
        product_name = row["product__name"] or ""
        type_name = row["product_type__name"] or ""
        unit_name = row["product__unit__name"] or ""
        income_value = _to_float(row["income"])

        product_entry = product_map.setdefault(
            product_name,
            {
                "product": product_name,
                "income": 0.0,
                "breakdown": {},
            },
        )
        breakdown_key = (type_name, unit_name)
        breakdown_entry = product_entry["breakdown"].setdefault(
            breakdown_key,
            {
                "type": type_name,
                "unit": unit_name,
                "income": 0.0,
            },
        )

        product_entry["income"] += income_value
        breakdown_entry["income"] += income_value

    data = []
    for product_name in sorted(product_map.keys(), key=lambda item: item or ""):
        product_entry = product_map[product_name]
        breakdown = []
        for breakdown_key in sorted(
            product_entry["breakdown"].keys(),
            key=lambda item: ((item[0] or ""), (item[1] or "")),
        ):
            breakdown.append(product_entry["breakdown"][breakdown_key])

        product_entry["breakdown"] = breakdown
        data.append(product_entry)

    return data


def _build_outcoming_product_stats(outcoming_rows):
    product_map = {}

    for row in outcoming_rows:
        product_name = row["product__name"] or ""
        type_name = row["type__name"] or ""
        unit_name = row["unit__name"] or ""
        outcoming_value = _to_float(row["outcoming"])

        product_entry = product_map.setdefault(
            product_name,
            {
                "product": product_name,
                "outcoming": 0.0,
                "breakdown": {},
            },
        )
        breakdown_key = (type_name, unit_name)
        breakdown_entry = product_entry["breakdown"].setdefault(
            breakdown_key,
            {
                "type": type_name,
                "unit": unit_name,
                "outcoming": 0.0,
            },
        )

        product_entry["outcoming"] += outcoming_value
        breakdown_entry["outcoming"] += outcoming_value

    data = []
    for product_name in sorted(product_map.keys(), key=lambda item: item or ""):
        product_entry = product_map[product_name]
        breakdown = []
        for breakdown_key in sorted(
            product_entry["breakdown"].keys(),
            key=lambda item: ((item[0] or ""), (item[1] or "")),
        ):
            breakdown.append(product_entry["breakdown"][breakdown_key])

        product_entry["breakdown"] = breakdown
        data.append(product_entry)

    return data


def _build_whouse_products_stats(income_rows, outcoming_rows):
    product_map = {}

    for row in income_rows:
        product_name = row["product__name"] or ""
        type_name = row["product_type__name"] or ""
        unit_name = row["product__unit__name"] or ""
        income_value = _to_float(row["income"])

        product_entry = product_map.setdefault(
            product_name,
            {
                "product": product_name,
                "income": 0.0,
                "outcoming": 0.0,
                "remaining": 0.0,
                "breakdown": {},
            },
        )
        breakdown_key = (type_name, unit_name)
        breakdown_entry = product_entry["breakdown"].setdefault(
            breakdown_key,
            {
                "type": type_name,
                "unit": unit_name,
                "income": 0.0,
                "outcoming": 0.0,
                "total": 0.0,
            },
        )

        product_entry["income"] += income_value
        breakdown_entry["income"] += income_value
        breakdown_entry["total"] += income_value

    for row in outcoming_rows:
        product_name = row["product__name"] or ""
        type_name = row["type__name"] or ""
        unit_name = row["unit__name"] or ""
        outcoming_value = _to_float(row["outcoming"])

        product_entry = product_map.setdefault(
            product_name,
            {
                "product": product_name,
                "income": 0.0,
                "outcoming": 0.0,
                "remaining": 0.0,
                "breakdown": {},
            },
        )
        breakdown_key = (type_name, unit_name)
        breakdown_entry = product_entry["breakdown"].setdefault(
            breakdown_key,
            {
                "type": type_name,
                "unit": unit_name,
                "income": 0.0,
                "outcoming": 0.0,
                "total": 0.0,
            },
        )

        product_entry["outcoming"] += outcoming_value
        breakdown_entry["outcoming"] += outcoming_value
        breakdown_entry["total"] += outcoming_value

    for product_name in product_map:
        product_entry = product_map[product_name]
        product_entry["remaining"] = product_entry["income"] - product_entry["outcoming"]
        for breakdown_key in product_entry["breakdown"]:
            bd = product_entry["breakdown"][breakdown_key]
            bd["total"] = bd["income"] - bd["outcoming"]

    data = []
    for product_name in sorted(product_map.keys(), key=lambda item: item or ""):
        product_entry = product_map[product_name]
        breakdown = []
        for breakdown_key in sorted(
            product_entry["breakdown"].keys(),
            key=lambda item: ((item[0] or ""), (item[1] or "")),
        ):
            breakdown.append(product_entry["breakdown"][breakdown_key])

        product_entry["breakdown"] = breakdown
        data.append(product_entry)

    return data


def calculate_status_durations(sub_orders):
    duration_totals = {}
    duration_counts = {}
    for sub_order in sub_orders:
        history = sub_order.status_history or []
        for i, entry in enumerate(history):
            if not isinstance(entry, dict):
                continue
            status_key = entry.get("status", "").upper()
            if not status_key or i + 1 >= len(history):
                continue
            next_entry = history[i + 1]
            if not isinstance(next_entry, dict):
                continue
            try:
                t1 = datetime.fromisoformat(str(entry["timestamp"]))
                t2 = datetime.fromisoformat(str(next_entry["timestamp"]))
                
                # Make both datetimes timezone-aware
                if t1.tzinfo is None:
                    t1 = timezone.make_aware(t1)
                if t2.tzinfo is None:
                    t2 = timezone.make_aware(t2)
                
                seconds = (t2 - t1).total_seconds()
                if seconds >= 0:
                    duration_totals[status_key] = (
                        duration_totals.get(status_key, 0) + seconds
                    )
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
        whouse_id = request.query_params.get("whouse")
        if not whouse_id:
            return {}
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return None
        return {"whouse": whouse}

    def whouse_not_found(self):
        return Response({"error": "Whouse not found"}, status=404)


class DateRangeFilterMixin:
    def get_date_filters(self, request, prefix=""):
        filters = {}
        start = request.query_params.get("start_date")
        end = request.query_params.get("end_date")
        field = f"{prefix}created_at__date"
        if start:
            try:
                filters[f"{field}__gte"] = date_type.fromisoformat(start)
            except ValueError:
                pass
        if end:
            try:
                filters[f"{field}__lte"] = date_type.fromisoformat(end)
            except ValueError:
                pass
        return filters


class OutcomingProductFilterMixin(DateRangeFilterMixin):
    def get_outcoming_product_filters(self, request, prefix=""):
        filters = self.get_date_filters(request, prefix)
        client = request.query_params.get("client")
        if client:
            filters[f"{prefix}client__id"] = client
        return filters


class CountStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_date_filters(request)
        return Response(
            {
                "drivers": Driver.objects.filter(**whouse_filter, **df).count(),
                "suppliers": Supplier.objects.filter(**whouse_filter, **df).count(),
                "clients": Client.objects.filter(**whouse_filter, **df).count(),
                "transports": Transport.objects.filter(**whouse_filter, **df).count(),
                "products": WhouseProducts.objects.filter(
                    **whouse_filter, **df
                ).count(),
                "orders": Order.objects.filter(**whouse_filter, **df).count(),
            }
        )


class ProductStatsBaseView(DateRangeFilterMixin, WhouseViewMixin):
    enable_supplier_filter = False
    enable_client_filter = False

    def get_income_rows(self, request, whouse_filter):
        filters = {"status": HistoryStatus.IN}
        if whouse_filter:
            filters["whouse"] = whouse_filter["whouse"]
        filters.update(self.get_date_filters(request))
        supplier_id = request.query_params.get("supplier")
        if self.enable_supplier_filter and supplier_id:
            filters["supplier__id"] = supplier_id
        return (
            WhouseProductsHistory.objects.filter(**filters)
            .values("product__name", "product_type__name", "product__unit__name")
            .annotate(income=Sum("quantity"))
            .order_by("product__name", "product_type__name", "product__unit__name")
        )

    def get_outcoming_rows(self, request, whouse_filter):
        filters = {}
        if whouse_filter:
            filters["order__whouse"] = whouse_filter["whouse"]
        filters.update(self.get_date_filters(request, prefix="order__"))
        client_id = request.query_params.get("client")
        if self.enable_client_filter and client_id:
            filters["order__client__id"] = client_id
        return (
            OrderItem.objects.filter(**filters)
            .values("product__name", "type__name", "unit__name")
            .annotate(outcoming=Sum("quantity"))
            .order_by("product__name", "type__name", "unit__name")
        )


class WhouseProductsStatsView(ProductStatsBaseView):
    serializer_class = WhouseProductsStatsSerializer

    @swagger_auto_schema(manual_parameters=WHOUSE_PARAM + DATE_RANGE_FILTER_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()

        income_rows = self.get_income_rows(request, whouse_filter)
        outcoming_rows = self.get_outcoming_rows(request, whouse_filter)
        data = _build_whouse_products_stats(income_rows, outcoming_rows)
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)

class IncomeProductStatsView(ProductStatsBaseView):
    enable_supplier_filter = True
    serializer_class = IncomeProductStatsSerializer

    @swagger_auto_schema(manual_parameters=INCOME_PRODUCT_FILTER_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()

        income_rows = self.get_income_rows(request, whouse_filter)
        data = _build_income_product_stats(income_rows)
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)


class OutcomingProductStatsView(ProductStatsBaseView):
    enable_client_filter = True
    serializer_class = OutcomingProductStatsSerializer

    @swagger_auto_schema(manual_parameters=OUTCOMING_PRODUCT_FILTER_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()

        outcoming_rows = self.get_outcoming_rows(request, whouse_filter)
        data = _build_outcoming_product_stats(outcoming_rows)
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data)


class OrderStatusStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()
        df = self.get_date_filters(request)
        qs = Order.objects.filter(**whouse_filter, **df)
        status_counts = {
            "total": qs.count(),
            "new": qs.filter(status=Order.Status.NEW).count(),
            "on_way": qs.filter(status=Order.Status.ON_WAY).count(),
            "arrived": qs.filter(status=Order.Status.ARRIVED).count(),
            "unloading": qs.filter(status=Order.Status.UNLOADING).count(),
            "completed": qs.filter(status=Order.Status.COMPLETED).count(),
            "rejected": qs.filter(status=Order.Status.REJECTED).count(),
        }

        if whouse_filter:
            whouse_filter = {"order__whouse": whouse_filter["whouse"]}
        df = self.get_date_filters(request, prefix="order__")
        sub_orders = SubOrder.objects.filter(**whouse_filter, **df).exclude(
            status_history=[]
        )
        avg = calculate_status_durations(sub_orders)
        status_durations = {
            "total": sub_orders.count(),
            "new": avg("NEW"),
            "on_way": avg("ON_WAY"),
            "arrived": avg("ARRIVED"),
            "unloading": avg("UNLOADING"),
            "completed": avg("COMPLETED"),
            "rejected": avg("REJECTED"),
        }
        result = {"status_counts": status_counts, "status_durations": status_durations}
        serializer = OrderStatsSerializer(result)
        return Response(serializer.data)


class ExcavatorOrderStatusStatsView(DateRangeFilterMixin, WhouseViewMixin):
    @swagger_auto_schema(manual_parameters=DATE_RANGE_PARAMS)
    def get(self, request):
        whouse_filter = self.get_whouse_filter(request)
        if whouse_filter is None:
            return self.whouse_not_found()

        df = self.get_date_filters(request)
        qs = ExcavatorOrder.objects.filter(**whouse_filter, **df)
        status_counts = {
            "total": qs.count(),
            "new": qs.filter(status=ExcavatorOrder.Status.NEW).count(),
            "in_progress": qs.filter(status=ExcavatorOrder.Status.IN_PROGRESS).count(),
            "paused": qs.filter(status=ExcavatorOrder.Status.PAUSED).count(),
            "completed": qs.filter(status=ExcavatorOrder.Status.COMPLETED).count(),
            "expired": qs.filter(status=ExcavatorOrder.Status.EXPIRED).count(),
            "rejected": qs.filter(status=ExcavatorOrder.Status.REJECTED).count(),
        }
        if whouse_filter:
            whouse_filter = {"parent__whouse": whouse_filter["whouse"]}

        sub_orders = ExcavatorSubOrder.objects.filter(**df, **whouse_filter).exclude(
            status_history=[]
        )
        avg = calculate_status_durations(sub_orders)
        status_durations = {
            "total": sub_orders.count(),
            "new": avg("NEW"),
            "in_progress": avg("IN_PROGRESS"),
            "paused": avg("PAUSED"),
            "completed": avg("COMPLETED"),
            "expired": avg("EXPIRED"),
            "rejected": avg("REJECTED"),
        }
        result = {"status_counts": status_counts, "status_durations": status_durations}
        serializer = ExcavatorOrderStatsSerializer(result)
        return Response(serializer.data)

from django.shortcuts import render
from rest_framework.views import APIView
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
from data.products.models import Product, WhouseProducts, WhouseProductsHistory
from data.supplier.models import Supplier
from apps.drivers.models import Driver
from data.clients.models import Client
from data.transports.models import Transport
from data.orders.models import Order, SubOrder
from data.excavator.models import ExcavatorOrder, ExcavatorSubOrder
from rest_framework.response import Response
from django.db.models import Sum
from data.whouse.models import Whouse

class CountStatsView(APIView):
    def get(self, request, whouse_id):
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return Response({'error': 'Whouse not found'}, status=404)
        drivers_count = Driver.objects.filter(whouse=whouse).count()
        suppliers_count = Supplier.objects.filter(whouse=whouse).count()
        clients_count = Client.objects.filter(whouse=whouse).count()
        transports_count = Transport.objects.filter(whouse=whouse).count()
        products_count = WhouseProducts.objects.filter(whouse=whouse).count()
        orders_count = Order.objects.filter(whouse=whouse).count()
        
        return Response({
            'drivers': drivers_count,
            'suppliers': suppliers_count,
            'clients': clients_count,
            'transports': transports_count,
            'products': products_count,
            'orders': orders_count,
        })

class IncomeProductStatsView(APIView):
    def get(self, request, whouse_id):
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return Response({'error': 'Whouse not found'}, status=404)
        products = Product.objects.filter(whouse=whouse, items__isnull=True)
        result = []
        for product in products:
            total_income = WhouseProducts.objects.filter(product=product, whouse=whouse, status=WhouseProducts.Status.IN).aggregate(total=Sum('quantity'))['total'] or 0
            result.append({
                'product': product.name,
                'income': total_income
            })
        serializer = IncomeProductStatsSerializer(result, many=True)
        return Response(serializer.data)

class OutcomingProductStatsView(APIView):
    def get(self, request, whouse_id):
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return Response({'error': 'Whouse not found'}, status=404)
        products = Product.objects.filter(whouse=whouse)
        result = []
        for product in products:
            total_income = WhouseProductsHistory.objects.filter(product=product, whouse=whouse, status=WhouseProductsHistory.Status.OUT).aggregate(total=Sum('quantity'))['total'] or 0
            result.append({
                'product': product.name,
                'outcome': total_income
            })
        serializer = OutcomingProductStatsSerializer(result, many=True)
        return Response(serializer.data)

class SupplierIncomeProductStatsView(APIView):
    def get(self, request, whouse_id):
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return Response({'error': 'Whouse not found'}, status=404)
        suppliers = Supplier.objects.filter(whouse=whouse)
        result = []
        for supplier in suppliers:
            total = 0
            products = Product.objects.filter(whouse=whouse, items__isnull=True)
            product_result = []
            for product in products:
                total_income = WhouseProductsHistory.objects.filter(product=product, whouse=whouse, supplier=supplier, status=WhouseProductsHistory.Status.IN).aggregate(total=Sum('quantity'))['total'] or 0
                total += total_income
                product_result.append({
                    'product': product.name,
                    'income': total_income
                })
            result.append({
                'supplier': supplier.name,
                'total': total,
                'products': product_result,
            })
        serializer = SupplierIncomeProductStatsSerializer(result, many=True)
        return Response(serializer.data)

class OrderStatusStatsView(APIView):
    def get(self, request, whouse_id):
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return Response({'error': 'Whouse not found'}, status=404)
        new_orders_count = Order.objects.filter(whouse=whouse, status=Order.Status.NEW).count()
        in_progress_orders_count = Order.objects.filter(whouse=whouse, status=Order.Status.IN_PROGRESS).count()
        on_way_orders_count = Order.objects.filter(whouse=whouse, status=Order.Status.ON_WAY).count()
        arrived_orders_count = Order.objects.filter(whouse=whouse, status=Order.Status.ARRIVED).count()
        unloading_orders_count = Order.objects.filter(whouse=whouse, status=Order.Status.UNLOADING).count()
        completed_orders_count = Order.objects.filter(whouse=whouse, status=Order.Status.COMPLETED).count()
        total_orders_count = Order.objects.filter(whouse=whouse).count()
        result = {
            'new': new_orders_count,
            'in_progress': in_progress_orders_count,
            'on_way': on_way_orders_count,
            'arrived': arrived_orders_count,
            'unloading': unloading_orders_count,
            'completed': completed_orders_count,
            'total': total_orders_count,
        }
        serializer = OrderStatusStatsSerializer(result)
        return Response(serializer.data)

class OrderStatusDurationStatsView(APIView):
    def get(self, request, whouse_id):
        whouse = Whouse.objects.filter(id=whouse_id).first()
        if not whouse:
            return Response({'error': 'Whouse not found'}, status=404)

        from datetime import datetime
        sub_orders = SubOrder.objects.filter(order__whouse=whouse).exclude(status_history=[])

        duration_totals = {}
        duration_counts = {}

        for sub_order in sub_orders:
            history = sub_order.status_history or []
            for i, entry in enumerate(history):
                status_key = entry.get('status', '').upper()
                if not status_key or i + 1 >= len(history):
                    continue
                try:
                    t1 = datetime.fromisoformat(str(entry['timestamp']))
                    t2 = datetime.fromisoformat(str(history[i + 1]['timestamp']))
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

        result = {
            'new': avg('NEW'),
            'in_progress': avg('IN_PROGRESS'),
            'on_way': avg('ON_WAY'),
            'arrived': avg('ARRIVED'),
            'unloading': avg('UNLOADING'),
            'completed': avg('COMPLETED'),
            'sub_orders_count': sub_orders.count(),
        }
        serializer = StatusDurationSerializer(result)
        return Response(serializer.data)


class ExcavatorOrderStatusStatsView(APIView):
    def get(self, request):
        result = {
            'new': ExcavatorOrder.objects.filter(status=ExcavatorOrder.Status.NEW).count(),
            'in_progress': ExcavatorOrder.objects.filter(status=ExcavatorOrder.Status.IN_PROGRESS).count(),
            'paused': ExcavatorOrder.objects.filter(status=ExcavatorOrder.Status.PAUSED).count(),
            'completed': ExcavatorOrder.objects.filter(status=ExcavatorOrder.Status.COMPLETED).count(),
            'expired': ExcavatorOrder.objects.filter(status=ExcavatorOrder.Status.EXPIRED).count(),
            'total': ExcavatorOrder.objects.count(),
        }
        serializer = ExcavatorOrderStatusStatsSerializer(result)
        return Response(serializer.data)


class ExcavatorStatusDurationStatsView(APIView):
    def get(self, request):
        from datetime import datetime
        sub_orders = ExcavatorSubOrder.objects.exclude(status_history=[])

        duration_totals = {}
        duration_counts = {}

        for sub_order in sub_orders:
            history = sub_order.status_history or []
            for i, entry in enumerate(history):
                status_key = entry.get('status', '').upper()
                if not status_key or i + 1 >= len(history):
                    continue
                try:
                    t1 = datetime.fromisoformat(str(entry['timestamp']))
                    t2 = datetime.fromisoformat(str(history[i + 1]['timestamp']))
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

        result = {
            'new': avg('NEW'),
            'in_progress': avg('IN_PROGRESS'),
            'paused': avg('PAUSED'),
            'completed': avg('COMPLETED'),
            'expired': avg('EXPIRED'),
            'sub_orders_count': sub_orders.count(),
        }
        serializer = ExcavatorStatusDurationSerializer(result)
        return Response(serializer.data)
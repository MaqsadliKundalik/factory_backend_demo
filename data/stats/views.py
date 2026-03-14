from django.shortcuts import render
from rest_framework.views import APIView
from data.stats.serializers import (
    SimpleCountStatsSerializer, 
    IncomeProductStatsSerializer, 
    SupplierIncomeProductStatsSerializer, 
    OutcomingProductStatsSerializer,
    OrderStatusStatsSerializer,
)
from data.products.models import Product, WhouseProducts, WhouseProductsHistory
from data.supplier.models import Supplier
from apps.drivers.models import Driver
from data.clients.models import Client
from data.transports.models import Transport
from data.orders.models import Order, SubOrder
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
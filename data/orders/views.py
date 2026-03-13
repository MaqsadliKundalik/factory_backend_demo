from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS

from .models import Order, SubOrder
from .serialziers import (
    OrderSerializer, OrderWriteSerializer,
    SubOrderSerializer, StatusHistorySerializer, CompetedStatusSerializer,
)
from data.filedatas.models import File


ORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter('client', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Client ID"),
    openapi.Parameter('branch', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Branch ID"),
    openapi.Parameter('whouse', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Warehouse ID"),
    openapi.Parameter('product', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Product ID"),
    openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Product Type ID"),
    openapi.Parameter('unit', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Product Unit ID"),
    openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"),
]

SUBORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter('order', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Order ID"),
    openapi.Parameter('driver', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Driver ID"),
    openapi.Parameter('transport', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Transport ID"),
    openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"),
    openapi.Parameter('in_progress', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description="Filter: true for active, false for completed"),
]


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderFilter(BaseDateFilterSet):
    class Meta:
        model = Order
        fields = ['client', 'branch', 'whouse', 'product', 'type', 'unit', 'status']


class SubOrderFilter(BaseDateFilterSet):
    in_progress = filters.BooleanFilter(method='filter_in_progress', label="Filter: true for active, false for completed")

    def filter_in_progress(self, queryset, name, value):
        if value is True:
            return queryset.exclude(status=SubOrder.Status.COMPLETED)
        elif value is False:
            return queryset.filter(status=SubOrder.Status.COMPLETED)
        return queryset

    class Meta:
        model = SubOrder
        fields = ['order', 'driver', 'transport', 'status']


class OrderViewSet(PermissionMetaMixin, ModelViewSet):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="ORDERS_PAGE", read_perm="ORDERS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrderFilter
    search_fields = ['display_id', 'client__name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Order.objects.none()
        if hasattr(user, 'whouses') and user.whouses.exists():
            return Order.objects.filter(whouse__in=user.whouses.all())
        return Order.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return OrderWriteSerializer
        return OrderSerializer

    @swagger_auto_schema(manual_parameters=ORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=OrderWriteSerializer, responses={201: OrderSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=OrderWriteSerializer, responses={200: OrderSerializer})
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data)


class SubOrderViewSet(PermissionMetaMixin, ModelViewSet):
    serializer_class = SubOrderSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="ORDERS_PAGE", read_perm="ORDERS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SubOrderFilter
    search_fields = ['order__display_id', 'driver__name', 'transport__model']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return SubOrder.objects.none()
        if hasattr(user, 'whouses') and user.whouses.exists():
            return SubOrder.objects.filter(order__whouse__in=user.whouses.all())
        if user.__class__.__name__ == 'Driver':
            return SubOrder.objects.filter(driver=user)
        return SubOrder.objects.all()

    @swagger_auto_schema(manual_parameters=SUBORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=StatusHistorySerializer(many=True),
        responses={200: "Successfully updated status history"}
    )
    @action(detail=True, methods=['post'], url_path='update-status-history')
    def update_status_history(self, request, pk=None):
        instance = self.get_object()
        serializer = StatusHistorySerializer(data=request.data, many=True)
        if serializer.is_valid():
            history = instance.status_history or []
            history.extend(serializer.data)
            instance.status_history = history
            instance.status = serializer.data[-1]['status']
            instance.save()
            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        consumes=['multipart/form-data'],
        request_body=CompetedStatusSerializer(),
        manual_parameters=[
            openapi.Parameter('files', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description="Files (repeat for multiple)"),
        ],
        responses={200: "Successfully updated completed status"}
    )
    @action(detail=True, methods=['post'], url_path='update-completed-status', parser_classes=[MultiPartParser, FormParser])
    def update_completed_status(self, request, pk=None):
        instance = self.get_object()
        serializer = CompetedStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        instance.status = SubOrder.Status.COMPLETED
        instance.status_history = instance.status_history or []
        instance.status_history.append({
            "status": "completed",
            "timestamp": str(serializer.validated_data.get("timestamp")),
        })

        if 'sign' in serializer.validated_data:
            instance.sign = File.objects.create(file=serializer.validated_data['sign'])

        for f in request.FILES.getlist('files'):
            file_obj = File.objects.create(file=f)
            instance.files.add(file_obj)

        instance.save()
        return Response({"status": "Success"}, status=status.HTTP_200_OK)

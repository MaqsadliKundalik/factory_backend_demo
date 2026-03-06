from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin, DateFilterSchemaMixin
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS

from .models import Order, SubOrder
from .serialziers import OrderSerializer, SubOrderSerializer, StatusHistorySerializer

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

class OrderViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
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

    @swagger_auto_schema(manual_parameters=DATE_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



class SubOrderViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = SubOrder.objects.all()
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
        return SubOrder.objects.all()

    @swagger_auto_schema(manual_parameters=DATE_FILTER_PARAMS)
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
            instance.save()
            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

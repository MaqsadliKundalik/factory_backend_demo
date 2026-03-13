from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS

from data.filedatas.models import File

from .models import ExcavatorOrder, ExcavatorSubOrder
from .serializers import (
    ExcavatorOrderSerializer,
    ExcavatorOrderCreateSerializer,
    ExcavatorSubOrderSerializer,
    ChangeStatusSerializer,
    StartOrderSerializer,
    FinishOrderSerializer,
    ExcavatorStatsSerializer,
)

EXCAVATOR_ORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"),
    openapi.Parameter('payment_status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Payment status"),
]

EXCAVATOR_SUBORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter('parent', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Parent order ID"),
    openapi.Parameter('driver', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Driver ID"),
    openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"),
    openapi.Parameter('transport_type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Transport type (transport.type)"),
]


def _save_files(file_list, m2m_field):
    for f in file_list:
        file_obj = File.objects.create(file=f)
        m2m_field.add(file_obj)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ExcavatorOrderFilter(BaseDateFilterSet):
    class Meta:
        model = ExcavatorOrder
        fields = ['status', 'payment_status']


class ExcavatorSubOrderFilter(BaseDateFilterSet):
    transport_type = filters.CharFilter(field_name='transport__type', lookup_expr='iexact')

    class Meta:
        model = ExcavatorSubOrder
        fields = ['parent', 'driver', 'status', 'transport']


class ExcavatorOrderViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ExcavatorOrder.objects.all()
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="ORDERS_PAGE", read_perm="ORDERS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ExcavatorOrderFilter
    search_fields = ['display_id', 'client_name', 'phone_number']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExcavatorOrderCreateSerializer
        return ExcavatorOrderSerializer

    @swagger_auto_schema(manual_parameters=EXCAVATOR_ORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: ExcavatorStatsSerializer()})
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = ExcavatorOrder.objects.all()
        data = {
            'total': qs.count(),
            'new': qs.filter(status=ExcavatorOrder.Status.NEW).count(),
            'in_progress': qs.filter(status=ExcavatorOrder.Status.IN_PROGRESS).count(),
            'paused': qs.filter(status=ExcavatorOrder.Status.PAUSED).count(),
            'completed': qs.filter(status=ExcavatorOrder.Status.COMPLETED).count(),
            'expired': qs.filter(status=ExcavatorOrder.Status.EXPIRED).count(),
            'paid': qs.filter(payment_status=ExcavatorOrder.PaymentStatus.PAID).count(),
            'pending_payment': qs.filter(payment_status=ExcavatorOrder.PaymentStatus.PENDING).count(),
        }
        return Response(data)

class ExcavatorSubOrderViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ExcavatorSubOrder.objects.all()
    serializer_class = ExcavatorSubOrderSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="ORDERS_PAGE", read_perm="ORDERS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ExcavatorSubOrderFilter
    search_fields = ['driver__name', 'transport__number']

    @swagger_auto_schema(manual_parameters=EXCAVATOR_SUBORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(request_body=ChangeStatusSerializer, responses={200: "Status updated"})
    @action(detail=True, methods=['patch'], url_path='change-status')
    def change_status(self, request, pk=None):
        instance = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        timestamp = serializer.validated_data['timestamp']

        user = request.user
        instance.status_history = instance.status_history or []
        
        instance.status_history.append({
            'old_status': instance.status,
            'new_status': new_status,
            'changed_at': str(timestamp),
            'changed_by': str(user.id),
            'changed_by_name': getattr(user, 'name', str(user)),
        })
        instance.status = new_status
        instance.save(update_fields=['status', 'status_history'])
        return Response({'status': instance.status})

    @swagger_auto_schema(
        consumes=['multipart/form-data'],
        request_body=StartOrderSerializer,
        manual_parameters=[
            openapi.Parameter('files', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description="Before photos"),
        ],
        responses={200: "Sub-order started"}
    )
    @action(detail=True, methods=['post'], url_path='start', parser_classes=[MultiPartParser, FormParser])
    def start(self, request, pk=None):
        instance = self.get_object()
        serializer = StartOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        sign = serializer.validated_data.get('sign')
        timestamp = serializer.validated_data.get('timestamp')
        
        if sign:
            instance.before_sign = File.objects.create(file=sign)

        _save_files(request.FILES.getlist('files'), instance.before_files)

        instance.status_history = instance.status_history or []
        instance.status_history.append({
            'old_status': instance.status,
            'new_status': ExcavatorSubOrder.Status.IN_PROGRESS,
            'changed_at': str(timestamp),
            'changed_by': str(user.id),
            'changed_by_name': getattr(user, 'name', str(user)),
        })
        instance.status = ExcavatorSubOrder.Status.IN_PROGRESS
        instance.save()
        return Response({'status': instance.status})

    @swagger_auto_schema(
        consumes=['multipart/form-data'],
        request_body=FinishOrderSerializer,
        manual_parameters=[
            openapi.Parameter('files', openapi.IN_FORM, type=openapi.TYPE_FILE, required=False, description="After photos"),
        ],
        responses={200: "Sub-order completed"}
    )
    @action(detail=True, methods=['post'], url_path='finish', parser_classes=[MultiPartParser, FormParser])
    def finish(self, request, pk=None):
        instance = self.get_object()
        serializer = FinishOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        timestamp = serializer.validated_data.get('timestamp')

        user = request.user
        sign = serializer.validated_data.get('sign')
        if sign:
            instance.after_sign = File.objects.create(file=sign)

        _save_files(request.FILES.getlist('files'), instance.after_files)

        instance.status_history = instance.status_history or []
        instance.status_history.append({
            'old_status': instance.status,
            'new_status': ExcavatorSubOrder.Status.COMPLETED,
            'changed_at': str(timestamp),
            'changed_by': str(user.id),
            'changed_by_name': getattr(user, 'name', str(user)),
        })
        instance.status = ExcavatorSubOrder.Status.COMPLETED
        instance.save()
        return Response({'status': instance.status})

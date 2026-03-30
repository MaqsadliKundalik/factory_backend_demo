from rest_framework.viewsets import ModelViewSet
from .models import Transport
from .serializers import TransportSerializer, SelectTransportSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.filters import BaseDateFilterSet
from apps.common.mixins import PermissionMetaMixin, DateFilterSchemaMixin
from rest_framework.pagination import PageNumberPagination
from data.excavator.models import ExcavatorSubOrder
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from data.orders.models import SubOrder
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

TRANSPORT_FILTER_PARAMS = [
    openapi.Parameter(
        "hasOrder",
        openapi.IN_QUERY,
        type=openapi.TYPE_BOOLEAN,
        description="Filter by order presence",
    ),
    openapi.Parameter(
        "type",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Filter by type",
    ),
    openapi.Parameter(
        "car_type",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Filter by car type",
    ),
    openapi.Parameter(
        "whouse",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_UUID,
        description="Filter by whouse",
    ),
]


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TransportFilter(BaseDateFilterSet):
    class Meta:
        model = Transport
        fields = ["whouse", "type", "car_type", "created_at", "updated_at"]


class TransportViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="TRANSPORTS_PAGE", read_perm="TRANSPORTS_PAGE")
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransportFilter
    search_fields = ["name", "number"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Transport.objects.none()

        whouses = user.whouses.all()
        return Transport.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        whouse_id = self.request.data.get("whouse")
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)


class TransportSelectView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="TRANSPORTS_PAGE", read_perm="TRANSPORTS_PAGE")
    ]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        operation_summary="Select transports (id and name only)",
        responses={200: SelectTransportSerializer(many=True)},
        manual_parameters=TRANSPORT_FILTER_PARAMS,
    )
    def get(self, request):
        has_order = request.query_params.get("hasOrder")
        transport_type = request.query_params.get("type")
        car_type = request.query_params.get("car_type")
        whouse = request.query_params.get("whouse")

        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if not user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)

        queryset = Transport.objects.all()

        if has_order:
            queryset = queryset.exclude(
                sub_orders__status__in=[
                    SubOrder.Status.ARRIVED,
                    SubOrder.Status.ON_WAY,
                    SubOrder.Status.UNLOADING,
                ]
            )
            queryset = queryset.exclude(
                excavator_sub_orders__status__in=[
                    ExcavatorSubOrder.Status.PAUSED,
                    ExcavatorSubOrder.Status.IN_PROGRESS,
                ]
            )
        if car_type:
            queryset = queryset.filter(car_type=car_type)
        if transport_type:
            queryset = queryset.filter(type=transport_type)
        if whouse:
            queryset = queryset.filter(whouse_id=whouse)

        data = queryset.values("id", "name", "number", "car_type")
        return Response(list(data))

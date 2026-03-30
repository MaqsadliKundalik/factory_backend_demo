from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from data.drivers.models import Driver
from data.orders.models import Order, SubOrder
from data.excavator.models import ExcavatorOrder, ExcavatorSubOrder

from data.drivers.serializers import (
    DriverSerializer,
    DriverPasswordChangeSerializer,
    SelectDriverSerializer,
)
from apps.common.permissions import HasDynamicPermission
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.mixins import PermissionMetaMixin
from rest_framework.pagination import PageNumberPagination
from apps.common.filters import BaseDateFilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


DRIVER_FILTER_PARAMS = [
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


class DriverFilter(BaseDateFilterSet):
    class Meta:
        model = Driver
        fields = ["whouse", "type", "created_at", "updated_at"]


class DriverViewSet(PermissionMetaMixin, ModelViewSet):
    authentication_classes = [UnifiedJWTAuthentication]
    serializer_class = DriverSerializer
    permission_classes = [
        HasDynamicPermission(crud_perm="TRANSPORTS_PAGE", read_perm="TRANSPORTS_PAGE")
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DriverFilter
    search_fields = ["name", "phone_number"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Driver.objects.none()
        return Driver.objects.filter(whouse__in=user.whouses.all())

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
            serializer.save(whouse=user.whouses.first())


class DriverSelectView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="DRIVERS_PAGE", read_perm="DRIVERS_PAGE")
    ]
    ordering = ["-created_at"]

    @swagger_auto_schema(
        operation_summary="Select drivers (id and name only)",
        responses={200: SelectDriverSerializer(many=True)},
        manual_parameters=DRIVER_FILTER_PARAMS,
    )
    def get(self, request):
        has_order = request.query_params.get("hasOrder")
        driver_type = request.query_params.get("type")
        whouse = request.query_params.get("whouse")

        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if not user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)

        queryset = Driver.objects.all()

        search = request.query_params.get("search")

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
                    ExcavatorSubOrder.Status.ARRIVED,
                    ExcavatorSubOrder.Status.PAUSED,
                    ExcavatorSubOrder.Status.IN_PROGRESS,
                ]
            )
        if driver_type:
            queryset = queryset.filter(type=driver_type)
        if whouse:
            queryset = queryset.filter(whouse_id=whouse)

        data = queryset.values("id", "name", "phone_number")
        return Response(list(data))


class DriverPasswordChangeView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="DRIVERS_PAGE", read_perm="DRIVERS_PAGE")
    ]

    @swagger_auto_schema(
        operation_summary="Изменение пароля водителя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["new_password"],
            properties={
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Новый пароль"
                ),
            },
        ),
        responses={
            200: "Пароль успешно изменен",
            400: "Неверные данные",
            404: "Водитель не найден",
        },
    )
    def post(self, request, driver_id):
        try:
            user = (
                request.driver or request.guard or request.operator or request.manager
            )
            if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
                return Response(
                    {"error": "Требуется аутентификация"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if user.__class__.__name__ == "Driver" and str(user.id) != str(driver_id):
                return Response(
                    {"error": "Вы можете изменить только свой пароль"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            whouses = user.whouses.all()
            driver = Driver.objects.filter(id=driver_id, whouse__in=whouses).first()

            if not driver:
                return Response(
                    {"error": "Водитель не найден"}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = DriverPasswordChangeSerializer(
                data=request.data, context={"driver": driver}
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Пароль успешно изменен"}, status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

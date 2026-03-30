from django.utils import timezone
from json import loads, JSONDecodeError
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
from apps.common.mixins import PermissionMetaMixin
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS
from data.clients.models import Client
from data.users.models import FactoryUser
from data.files.models import File

from .models import ExcavatorOrder, ExcavatorSubOrder
from .serializers import (
    ExcavatorOrderSerializer,
    ExcavatorOrderCreateSerializer,
    ExcavatorSubOrderSerializer,
    ChangeStatusSerializer,
    StartOrderSerializer,
    FinishOrderSerializer,
    ExcavatorSubOrderListSerializer,
    RejectOrderSerializer,
)

EXCAVATOR_ORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter(
        "status", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"
    ),
    openapi.Parameter(
        "payment_status",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Payment status",
    ),
    openapi.Parameter(
        "whouse", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Whouse ID"
    ),
]

EXCAVATOR_SUBORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter(
        "parent",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Parent order ID",
    ),
    openapi.Parameter(
        "driver", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Driver ID"
    ),
    openapi.Parameter(
        "status", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"
    ),
    openapi.Parameter(
        "transport_type",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Transport type (transport.type)",
    ),
    openapi.Parameter(
        "in_progress",
        openapi.IN_QUERY,
        type=openapi.TYPE_BOOLEAN,
        description="Filter: true for active, false for completed",
    ),
]


def _normalize_file_ids(data):
    file_ids = []

    if hasattr(data, "getlist"):
        file_ids.extend(data.getlist("files"))
        file_ids.extend(data.getlist("files[]"))
        file_ids.extend(data.getlist("file_ids"))
        file_ids.extend(data.getlist("file_ids[]"))

    direct_value = data.get("files")
    bracket_value = data.get("files[]")
    direct_ids_value = data.get("file_ids")
    bracket_ids_value = data.get("file_ids[]")

    for value in [direct_value, bracket_value, direct_ids_value, bracket_ids_value]:
        if not value:
            continue
        if isinstance(value, list):
            file_ids.extend(value)
            continue
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value.startswith("[") and stripped_value.endswith("]"):
                try:
                    parsed_value = loads(stripped_value)
                    if isinstance(parsed_value, list):
                        file_ids.extend(parsed_value)
                        continue
                except JSONDecodeError:
                    pass
        file_ids.append(value)

    normalized_ids = []
    seen = set()
    for file_id in file_ids:
        normalized_value = str(file_id).strip()
        if not normalized_value or normalized_value in seen:
            continue
        seen.add(normalized_value)
        normalized_ids.append(normalized_value)

    return normalized_ids


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ExcavatorOrderFilter(BaseDateFilterSet):
    class Meta:
        model = ExcavatorOrder
        fields = ["status", "payment_status", "whouse"]


class ExcavatorSubOrderFilter(BaseDateFilterSet):
    transport_type = filters.CharFilter(
        field_name="transport__type", lookup_expr="iexact"
    )
    in_progress = filters.BooleanFilter(
        method="filter_in_progress",
        label="Filter: true for active, false for completed",
    )

    def filter_in_progress(self, queryset, name, value):
        if value is True:
            return queryset.exclude(
                status__in=[
                    ExcavatorSubOrder.Status.COMPLETED,
                    ExcavatorSubOrder.Status.REJECTED,
                    ExcavatorSubOrder.Status.EXPIRED,
                ]
            )
        elif value is False:
            return queryset.filter(
                status__in=[
                    ExcavatorSubOrder.Status.COMPLETED,
                    ExcavatorSubOrder.Status.REJECTED,
                    ExcavatorSubOrder.Status.EXPIRED,
                ]
            )
        return queryset

    class Meta:
        model = ExcavatorSubOrder
        fields = ["parent", "driver", "status", "transport"]


class ExcavatorOrderViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ExcavatorOrder.objects.all()
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="EXCAVATORS_PAGE", read_perm="EXCAVATORS_PAGE")
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ExcavatorOrderFilter
    search_fields = ["display_id", "client_name", "phone_number"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExcavatorOrderCreateSerializer
        return ExcavatorOrderSerializer

    @swagger_auto_schema(manual_parameters=EXCAVATOR_ORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=RejectOrderSerializer, responses={200: "Reject order"}
    )
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        order = self.get_object()

        serializer = RejectOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rejector_role = serializer.validated_data["rejector_role"]
        rejector_id = serializer.validated_data["rejector_id"]
        user = None
        if rejector_role == ExcavatorOrder.Rejector.CLIENT:
            try:
                user = Client.objects.get(id=rejector_id)
            except Client.DoesNotExist:
                return Response(
                    {"detail": "Client not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            try:
                user = FactoryUser.objects.get(id=rejector_id)
            except FactoryUser.DoesNotExist:
                return Response(
                    {"detail": "Factory user not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        sub_orders = order.sub_orders.all()
        for sub_order in sub_orders:
            sub_order.status = ExcavatorSubOrder.Status.REJECTED
            sub_order.save()
        order.status = ExcavatorOrder.Status.REJECTED
        order.rejector_role = rejector_role
        order.rejector_id = rejector_id
        order.save()
        return Response({"detail": "Order rejected"}, status=status.HTTP_200_OK)


class ExcavatorSubOrderViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ExcavatorSubOrder.objects.all()
    serializer_class = ExcavatorSubOrderSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="EXCAVATORS_PAGE", read_perm="EXCAVATORS_PAGE")
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ExcavatorSubOrderFilter
    search_fields = ["driver__name", "transport__number"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if self.request.driver:
            return ExcavatorSubOrder.objects.filter(driver=self.request.driver)

        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return ExcavatorSubOrder.objects.none()
        if hasattr(user, "whouses") and user.whouses.exists():
            return ExcavatorSubOrder.objects.filter(
                parent__whouse__in=user.whouses.all()
            )
        return ExcavatorSubOrder.objects.all()

    @swagger_auto_schema(manual_parameters=EXCAVATOR_SUBORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        self.serializer_class = ExcavatorSubOrderListSerializer
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=ChangeStatusSerializer, responses={200: "Status updated"}
    )
    @action(detail=True, methods=["patch"], url_path="change-status")
    def change_status(self, request, pk=None):
        instance = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        timestamp = serializer.validated_data["timestamp"]

        user = request.driver or request.guard or request.operator or request.manager
        instance.status_history = instance.status_history or []

        instance.status_history.append(
            {
                "old_status": instance.status,
                "new_status": new_status,
                "changed_at": str(timestamp),
                "changed_by": str(user.id),
                "changed_by_name": getattr(user, "name", str(user)),
            }
        )
        instance.status = new_status
        instance.save(update_fields=["status", "status_history"])

        parent = instance.parent
        sibling_statuses = list(parent.sub_orders.values_list("status", flat=True))
        if sibling_statuses and all(s == new_status for s in sibling_statuses):
            parent.status = new_status
            parent.save(update_fields=["status"])

        return Response({"status": instance.status})

    @swagger_auto_schema(
        request_body=StartOrderSerializer, responses={200: "Sub-order started"}
    )
    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        instance = self.get_object()
        payload = request.data.copy()
        payload.setlist("files", _normalize_file_ids(request.data))
        serializer = StartOrderSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        user = request.driver or request.guard or request.operator or request.manager
        sign = serializer.validated_data.get("sign")
        timestamp = serializer.validated_data.get("timestamp")

        if sign:
            instance.before_sign_id = sign

        file_ids = serializer.validated_data.get("files", [])
        if file_ids:
            try:
                from data.files.models import File
                valid_files = File.objects.filter(id__in=file_ids)
                instance.before_files.set(valid_files)
            except Exception as e:
                print(f"[ERROR] Failed to set before_files: {e}")

        instance.status_history = instance.status_history or []
        instance.status_history.append(
            {
                "old_status": instance.status,
                "new_status": ExcavatorSubOrder.Status.IN_PROGRESS,
                "changed_at": str(timestamp),
                "changed_by": str(user.id),
                "changed_by_name": getattr(user, "name", str(user)),
            }
        )
        instance.status = ExcavatorSubOrder.Status.IN_PROGRESS
        instance.save()

        parent = instance.parent
        sibling_statuses = list(parent.sub_orders.values_list("status", flat=True))
        if sibling_statuses and all(
            s == ExcavatorSubOrder.Status.IN_PROGRESS for s in sibling_statuses
        ):
            parent.status = ExcavatorSubOrder.Status.IN_PROGRESS
            parent.save(update_fields=["status"])

        return Response({"status": instance.status})

    @swagger_auto_schema(
        request_body=FinishOrderSerializer, responses={200: "Sub-order completed"}
    )
    @action(detail=True, methods=["post"], url_path="finish")
    def finish(self, request, pk=None):
        instance = self.get_object()
        payload = request.data.copy()
        payload.setlist("files", _normalize_file_ids(request.data))
        serializer = FinishOrderSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        timestamp = serializer.validated_data.get("timestamp")

        user = request.driver or request.guard or request.operator or request.manager
        sign = serializer.validated_data.get("sign")
        if sign:
            instance.after_sign_id = sign

        file_ids = serializer.validated_data.get("files", [])
        if file_ids:
            try:
                from data.files.models import File
                valid_files = File.objects.filter(id__in=file_ids)
                instance.after_files.set(valid_files)
            except Exception as e:
                print(f"[ERROR] Failed to set after_files: {e}")

        instance.status_history = instance.status_history or []
        instance.status_history.append(
            {
                "old_status": instance.status,
                "new_status": ExcavatorSubOrder.Status.COMPLETED,
                "changed_at": str(timestamp),
                "changed_by": str(user.id),
                "changed_by_name": getattr(user, "name", str(user)),
            }
        )
        instance.status = ExcavatorSubOrder.Status.COMPLETED
        instance.save()

        parent = instance.parent
        sibling_statuses = list(parent.sub_orders.values_list("status", flat=True))
        if sibling_statuses and all(
            s == ExcavatorSubOrder.Status.COMPLETED for s in sibling_statuses
        ):
            parent.status = ExcavatorSubOrder.Status.COMPLETED
            parent.save(update_fields=["status"])

        return Response({"status": instance.status})


from ast import List
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


from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS

from .models import Order, OrderItem, SubOrder, SubOrderItem
from .serialziers import (
    OrderSerializer,
    OrderWriteSerializer,
    SubOrderSerializer,
    StatusHistorySerializer,
    CompetedStatusSerializer,
    SubOrderListSerializer,
    RejectOrderSerializer,
    OrderDetailSerializer,
)
from data.files.models import File


ORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter(
        "client", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Client ID"
    ),
    openapi.Parameter(
        "branch", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Branch ID"
    ),
    openapi.Parameter(
        "whouse", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Warehouse ID"
    ),
    openapi.Parameter(
        "product", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Product ID"
    ),
    openapi.Parameter(
        "payment_status",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Payment status",
        enum=Order.PaymentStatus.choices,
    ),
    openapi.Parameter(
        "type",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Product Type ID",
    ),
    openapi.Parameter(
        "unit",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Product Unit ID",
    ),
    openapi.Parameter(
        "status", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"
    ),
]

SUBORDER_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter(
        "order", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Order ID"
    ),
    openapi.Parameter(
        "driver", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Driver ID"
    ),
    openapi.Parameter(
        "transport",
        openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        description="Transport ID",
    ),
    openapi.Parameter(
        "status", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Status"
    ),
    openapi.Parameter(
        "in_progress",
        openapi.IN_QUERY,
        type=openapi.TYPE_BOOLEAN,
        description="Filter: true for active, false for completed",
    ),
]


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderFilter(BaseDateFilterSet):
    class Meta:
        model = Order
        fields = ["client", "branch", "whouse", "status", "payment_status"]


class SubOrderFilter(BaseDateFilterSet):
    in_progress = filters.BooleanFilter(
        method="filter_in_progress",
        label="Filter: true for active, false for completed",
    )

    def filter_in_progress(self, queryset, name, value):
        if value is True:
            return queryset.exclude(status__in=[SubOrder.Status.COMPLETED, SubOrder.Status.REJECTED])
        elif value is False:
            return queryset.filter(status__in=[SubOrder.Status.COMPLETED, SubOrder.Status.REJECTED])
        return queryset

    class Meta:
        model = SubOrder
        fields = ["order", "driver", "transport", "status"]


class OrderViewSet(PermissionMetaMixin, ModelViewSet):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="ORDERS_PAGE", read_perm="ORDERS_PAGE")
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrderFilter
    search_fields = ["display_id", "client__name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Order.objects.none()
        if hasattr(user, "whouses") and user.whouses.exists():
            return Order.objects.filter(whouse__in=user.whouses.all())
        return Order.objects.all()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return OrderWriteSerialize
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    @swagger_auto_schema(manual_parameters=ORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=OrderWriteSerializer, responses={201: OrderSerializer}
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=OrderWriteSerializer, responses={200: OrderSerializer}
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data)

    @swagger_auto_schema(
        request_body=RejectOrderSerializer,
        responses={200: OrderSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reject")
    @transaction.atomic
    def reject(self, request, *args, **kwargs):
        order = self.get_object()

        serializer = RejectOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rejector_role = serializer.validated_data["rejector_role"]
        order_items_data = serializer.validated_data["order_items"]

        user = (
            request.driver
            or request.guard
            or request.operator
            or request.manager
        )

        # Set rejector info
        order.rejector_role = rejector_role
        order.rejector_id = order.client.id if rejector_role == Order.Rejector.CLIENT else user.id

        # Prefetch order items and sub_order_items to avoid N+1
        item_ids = [item["order_item_id"] for item in order_items_data]
        order_items_map = {
            oi.id: oi for oi in OrderItem.objects.filter(id__in=item_ids, order=order)
        }

        sub_orders = list(
            order.sub_orders.select_related().prefetch_related("sub_order_items")
        )

        # Update order_item quantities and matching sub_order_items
        sub_order_items_to_update = []
        order_items_to_update = []

        for item_data in order_items_data:
            order_item = order_items_map.get(item_data["order_item_id"])
            if not order_item:
                continue

            quantity_to_deduct = item_data["quantity"]
            order_item.quantity = max(0, order_item.quantity - quantity_to_deduct)
            order_items_to_update.append(order_item)

            # Find matching suborder items and deduct quantity in order
            remaining_quantity = quantity_to_deduct
            
            for sub_order in sub_orders:
                if sub_order.status == SubOrder.Status.COMPLETED or remaining_quantity <= 0:
                    continue
                    
                # Find all matching suborder items in this suborder
                matching_items = [
                    soi for soi in sub_order.sub_order_items.all()
                    if (soi.product_id == order_item.product_id
                        and soi.type_id == order_item.type_id
                        and soi.unit_id == order_item.unit_id
                        and soi.quantity > 0)
                ]
                
                # Deduct from matching items in this suborder
                for matching_soi in matching_items:
                    if remaining_quantity <= 0:
                        break
                    
                    deduct_amount = min(remaining_quantity, matching_soi.quantity)
                    matching_soi.quantity = max(0, matching_soi.quantity - deduct_amount)
                    sub_order_items_to_update.append(matching_soi)
                    remaining_quantity -= deduct_amount

        # Bulk update quantities
        if order_items_to_update:
            OrderItem.objects.bulk_update(order_items_to_update, ["quantity"])
        if sub_order_items_to_update:
            SubOrderItem.objects.bulk_update(sub_order_items_to_update, ["quantity"])

        # Reject non-completed suborders
        for sub_order in order.sub_orders.exclude(
            status=SubOrder.Status.COMPLETED
        ):
            # Check if all items in this suborder have quantity 0
            all_items_zero = all(soi.quantity == 0 for soi in sub_order.sub_order_items.all())
            if all_items_zero:
                sub_order.status = SubOrder.Status.REJECTED
                sub_order.save(update_fields=["status"])

        # If all suborders are rejected or completed — set order status
        all_suborders_rejected_or_completed = all(
            so.status in [SubOrder.Status.REJECTED, SubOrder.Status.COMPLETED] 
            for so in order.sub_orders.all()
        )
        if all_suborders_rejected_or_completed:
            order.status = Order.Status.REJECTED
        order.save(update_fields=["status", "rejector_role", "rejector_id"])

        return Response(OrderSerializer(order).data)


class SubOrderViewSet(PermissionMetaMixin, ModelViewSet):
    serializer_class = SubOrderSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="ORDERS_PAGE", read_perm="ORDERS_PAGE")
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SubOrderFilter
    search_fields = ["order__display_id", "driver__name", "transport__model"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if self.request.driver:
            return SubOrder.objects.filter(driver=self.request.driver)
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return SubOrder.objects.none()
        if hasattr(user, "whouses") and user.whouses.exists():
            return SubOrder.objects.filter(order__whouse__in=user.whouses.all())
        return SubOrder.objects.all()

    @swagger_auto_schema(manual_parameters=SUBORDER_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        self.serializer_class = SubOrderListSerializer
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=StatusHistorySerializer(many=True),
        responses={200: "Successfully updated status history"},
    )
    @action(detail=True, methods=["post"], url_path="update-status-history")
    def update_status_history(self, request, pk=None):
        instance = self.get_object()

        serializer = StatusHistorySerializer(data=request.data, many=True)
        if serializer.is_valid():
            history = instance.status_history or []
            history.extend(serializer.data)
            instance.status_history = history
            new_status = serializer.data[-1]["status"]
            instance.status = new_status
            instance.save()

            order = instance.order
            sibling_statuses = list(order.sub_orders.values_list("status", flat=True))
            if sibling_statuses and all(s == new_status for s in sibling_statuses):
                order.status = new_status
                order.save(update_fields=["status"])

            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=CompetedStatusSerializer(),
        responses={200: "Successfully updated completed status"},
    )
    @action(detail=True, methods=["post"], url_path="update-completed-status")
    def update_completed_status(self, request, pk=None):
        instance = self.get_object()
        serializer = CompetedStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status = SubOrder.Status.COMPLETED
        instance.status = new_status
        instance.status_history = instance.status_history or []
        instance.status_history.append(
            {
                "status": new_status,
                "timestamp": str(serializer.validated_data.get("timestamp")),
            }
        )

        if "sign" in serializer.validated_data:
            instance.sign_id = serializer.validated_data["sign"]

        file_ids = serializer.validated_data.get("files", [])
        if file_ids:
            instance.files.set(file_ids)

        instance.save()

        order = instance.order
        sibling_statuses = list(order.sub_orders.values_list("status", flat=True))
        if sibling_statuses and all(s == new_status for s in sibling_statuses):
            order.status = new_status
            order.save(update_fields=["status"])

        return Response({"status": "Success"}, status=status.HTTP_200_OK)

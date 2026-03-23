from rest_framework import serializers
from .models import Order, SubOrder, OrderItem, SubOrderItem
from data.products.serializers import (
    ProductSerializer,
    ProductTypeSerializer,
    ProductUnitSerializer,
)
from data.clients.serializers import ClientSerializer, ClientBranchesSerializer
from data.drivers.serializers import DriverSerializer
from data.transports.serializers import TransportSerializer
from data.files.serializers import FileSerializer


class StatusHistorySerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return {
                "status": instance.get("status", ""),
                "timestamp": instance.get("timestamp"),
            }
        return super().to_representation(instance)


class CompetedStatusSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    sign = serializers.UUIDField(required=False)
    files = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )


# --- OrderItem serializers ---


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "type", "unit", "quantity", "price"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["product"] = ProductSerializer(instance.product).data
        rep["type"] = ProductTypeSerializer(instance.type).data
        rep["unit"] = ProductUnitSerializer(instance.unit).data
        return rep


class OrderItemWriteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "type", "unit", "quantity", "price"]


# --- SubOrderItem serializers ---


class SubOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubOrderItem
        fields = ["id", "product", "type", "unit", "quantity"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["product"] = ProductSerializer(instance.product).data
        rep["type"] = ProductTypeSerializer(instance.type).data
        rep["unit"] = ProductUnitSerializer(instance.unit).data
        return rep


class SubOrderItemWriteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = SubOrderItem
        fields = ["id", "product", "type", "unit", "quantity"]


# --- SubOrder serializers ---


class SubOrderInlineSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    sub_order_items = SubOrderItemWriteSerializer(many=True, required=False)

    class Meta:
        model = SubOrder
        fields = [
            "id",
            "driver",
            "transport",
            "quantity",
            "status",
            "status_history",
            "sign",
            "files",
            "sub_order_items",
        ]
        read_only_fields = ["status", "sign"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["driver"] = DriverSerializer(instance.driver).data
        rep["transport"] = TransportSerializer(instance.transport).data
        rep["files"] = FileSerializer(instance.files.all(), many=True).data
        rep["sign"] = FileSerializer(instance.sign).data if instance.sign else None
        rep["sub_order_items"] = SubOrderItemSerializer(
            instance.sub_order_items.all(), many=True
        ).data
        return rep


class SubOrderSerializer(serializers.ModelSerializer):
    status_history = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = SubOrder
        fields = [
            "id",
            "order",
            "driver",
            "transport",
            "quantity",
            "status",
            "status_history",
            "sign",
            "files",
        ]
        read_only_fields = ["id", "sign", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["order"] = {
            "id": instance.order.id,
            "display_id": instance.order.display_id,
            "client": ClientSerializer(instance.order.client).data,
            "branch": ClientBranchesSerializer(instance.order.branch).data,
            "whouse": {
                "id": instance.order.whouse.id,
                "name": instance.order.whouse.name,
            },
            "order_items": OrderItemSerializer(
                instance.order.order_items.all(), many=True
            ).data,
            "status": instance.order.status,
            "created_at": instance.order.created_at,
        }
        rep["driver"] = DriverSerializer(instance.driver).data
        rep["transport"] = TransportSerializer(instance.transport).data
        rep["sign"] = FileSerializer(instance.sign).data if instance.sign else None
        rep["files"] = FileSerializer(instance.files.all(), many=True).data
        return rep


# --- Order serializers ---


class OrderSerializer(serializers.ModelSerializer):
    sub_orders = SubOrderInlineSerializer(many=True, read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "display_id",
            "client",
            "branch",
            "whouse",
            "status",
            "rejector_role",
            "rejector_id",
            "order_items",
            "sub_orders",
            "created_at",
        ]
        read_only_fields = ["id", "display_id", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["client"] = ClientSerializer(instance.client).data
        rep["branch"] = ClientBranchesSerializer(instance.branch).data
        rep["whouse"] = {"id": instance.whouse.id, "name": instance.whouse.name}
        return rep


class OrderWriteSerializer(serializers.ModelSerializer):
    sub_orders = SubOrderInlineSerializer(many=True, required=False)
    order_items = OrderItemWriteSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "display_id",
            "client",
            "branch",
            "whouse",
            "status",
            "order_items",
            "sub_orders",
        ]
        read_only_fields = ["id", "display_id"]

    def create(self, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", [])
        order_items_data = validated_data.pop("order_items", [])
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            item_data.pop("id", None)
            OrderItem.objects.create(order=order, **item_data)
        for sub_data in sub_orders_data:
            sub_data.pop("id", None)
            sub_order_items_data = sub_data.pop("sub_order_items", [])
            sub_order = SubOrder.objects.create(order=order, **sub_data)
            for sub_item_data in sub_order_items_data:
                sub_item_data.pop("id", None)
                SubOrderItem.objects.create(sub_order=sub_order, **sub_item_data)
        return order

    def update(self, instance, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", None)
        order_items_data = validated_data.pop("order_items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if order_items_data is not None:
            incoming_ids = {item["id"] for item in order_items_data if "id" in item}
            instance.order_items.exclude(id__in=incoming_ids).delete()
            for item_data in order_items_data:
                item_id = item_data.pop("id", None)
                if item_id:
                    OrderItem.objects.filter(id=item_id, order=instance).update(**item_data)
                else:
                    OrderItem.objects.create(order=instance, **item_data)

        if sub_orders_data is not None:
            incoming_ids = {sub["id"] for sub in sub_orders_data if "id" in sub}
            instance.sub_orders.exclude(id__in=incoming_ids).delete()
            for sub_data in sub_orders_data:
                sub_order_items_data = sub_data.pop("sub_order_items", None)
                sub_id = sub_data.pop("id", None)
                if sub_id:
                    SubOrder.objects.filter(id=sub_id, order=instance).update(**sub_data)
                    sub_order = SubOrder.objects.get(id=sub_id)
                else:
                    sub_order = SubOrder.objects.create(order=instance, **sub_data)
                if sub_order_items_data is not None:
                    incoming_item_ids = {
                        item["id"] for item in sub_order_items_data if "id" in item
                    }
                    sub_order.sub_order_items.exclude(id__in=incoming_item_ids).delete()
                    for sub_item_data in sub_order_items_data:
                        sub_item_id = sub_item_data.pop("id", None)
                        if sub_item_id:
                            SubOrderItem.objects.filter(
                                id=sub_item_id, sub_order=sub_order
                            ).update(**sub_item_data)
                        else:
                            SubOrderItem.objects.create(
                                sub_order=sub_order, **sub_item_data
                            )

        return instance

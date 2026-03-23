from rest_framework import serializers
from .models import Order, SubOrder
from data.products.serializers import (
    ProductSerializer,
    ProductTypeSerializer,
    ProductUnitSerializer,
)
from data.clients.serializers import ClientSerializer, ClientBranchesSerializer
from data.drivers.serializers import DriverSerializer
from data.transports.models import Transport
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


# --- SubOrder serializers ---


class SubOrderInlineSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    status_history = StatusHistorySerializer(many=True, read_only=True)

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
        ]
        read_only_fields = ["status", "sign"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["driver"] = DriverSerializer(instance.driver).data
        rep["transport"] = TransportSerializer(instance.transport).data
        rep["files"] = FileSerializer(instance.files.all(), many=True).data
        rep["sign"] = FileSerializer(instance.sign).data if instance.sign else None
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
            "product": ProductSerializer(instance.order.product).data,
            "type": ProductTypeSerializer(instance.order.type).data,
            "unit": ProductUnitSerializer(instance.order.unit).data,
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

    class Meta:
        model = Order
        fields = [
            "id",
            "display_id",
            "client",
            "branch",
            "whouse",
            "product",
            "type",
            "unit",
            "status",
            "quantity",
            "sub_orders",
            "created_at",
            "price",
        ]
        read_only_fields = ["id", "display_id", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["client"] = ClientSerializer(instance.client).data
        rep["branch"] = ClientBranchesSerializer(instance.branch).data
        rep["whouse"] = {"id": instance.whouse.id, "name": instance.whouse.name}
        rep["product"] = ProductSerializer(instance.product).data
        rep["type"] = ProductTypeSerializer(instance.type).data
        rep["unit"] = ProductUnitSerializer(instance.unit).data
        if instance.rejector:
            rep["rejector"] = instance.rejector
        return rep


class OrderWriteSerializer(serializers.ModelSerializer):
    sub_orders = SubOrderInlineSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "display_id",
            "client",
            "branch",
            "whouse",
            "product",
            "type",
            "unit",
            "status",
            "quantity",
            "sub_orders",
            "price",
        ]
        read_only_fields = ["id", "display_id"]

    def create(self, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", [])
        order = Order.objects.create(**validated_data)
        for sub_data in sub_orders_data:
            sub_data.pop("id", None)
            SubOrder.objects.create(order=order, **sub_data)
        return order

    def update(self, instance, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if sub_orders_data is not None:
            incoming_ids = {sub["id"] for sub in sub_orders_data if "id" in sub}
            instance.sub_orders.exclude(id__in=incoming_ids).delete()
            for sub_data in sub_orders_data:
                sub_id = sub_data.pop("id", None)
                if sub_id:
                    SubOrder.objects.filter(id=sub_id, order=instance).update(
                        **sub_data
                    )
                else:
                    SubOrder.objects.create(order=instance, **sub_data)

        return instance

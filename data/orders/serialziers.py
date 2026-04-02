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

def _format_order_items_for_sms(order: Order):
    items = order.order_items.select_related("product", "type", "unit")
    return "\n".join(
        [
            "- {name} {type_name} ({quantity} {unit})".format(
                name=item.product.name,
                type_name=item.type.name,
                quantity=item.quantity,
                unit=item.unit.name,
            ).strip()
            for item in items
        ]
    )


class StatusHistorySerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return {
                "status": instance.get("status", ""),
                "timestamp": instance.get("timestamp"),
            }
        if isinstance(instance, str):
            return {
                "status": instance,
                "timestamp": None,
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


class OrderSummarySerializer(serializers.ModelSerializer):
    display_id = serializers.ReadOnlyField(source="get_display_id")
    client = ClientSerializer(read_only=True)
    branch = ClientBranchesSerializer(read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)
    whouse = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "display_id",
            "client",
            "branch",
            "whouse",
            "order_items",
            "status",
            "created_at",
        ]

    def get_whouse(self, instance):
        return {"id": instance.whouse.id, "name": instance.whouse.name}


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
            "status",
            "status_history",
            "sign",
            "files",
            "sub_order_items",
            "created_at",
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
            "status",
            "status_history",
            "sign",
            "files",
            "created_at",
        ]
        read_only_fields = ["id", "sign", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["order"] = OrderSummarySerializer(instance.order).data
        rep["driver"] = DriverSerializer(instance.driver).data
        rep["transport"] = TransportSerializer(instance.transport).data
        rep["sign"] = FileSerializer(instance.sign).data if instance.sign else None
        rep["files"] = FileSerializer(instance.files.all(), many=True).data
        return rep


class SubOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubOrder
        fields = [
            "id",
            "order",
            "status",
            "sign",
            "files",
            "status_history",
            "created_at",
        ]
        read_only_fields = ["id", "sign", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["order"] = OrderSummarySerializer(instance.order).data
        rep["sign"] = FileSerializer(instance.sign).data if instance.sign else None
        rep["files"] = FileSerializer(instance.files.all(), many=True).data
        return rep


# --- Order serializers ---


class OrderSerializer(serializers.ModelSerializer):
    display_id = serializers.ReadOnlyField(source="get_display_id")
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "display_id",
            "client",
            "branch",
            "payment_status",
            "order_type",
            "whouse",
            "status",
            "rejector_role",
            "rejector_id",
            "completion_percentage",
            "created_at",
        ]
        read_only_fields = ["id", "display_id", "created_at"]

    def get_completion_percentage(self, instance):
        order_items = list(instance.order_items.all())
        total_quantity = sum(float(item.quantity) for item in order_items)
        if total_quantity <= 0:
            return 0

        completed_quantity = 0
        for sub_order in instance.sub_orders.all():
            if sub_order.status != SubOrder.Status.COMPLETED:
                continue
            for sub_item in sub_order.sub_order_items.all():
                completed_quantity += float(sub_item.quantity)

        percentage = (completed_quantity / total_quantity) * 100
        return round(min(percentage, 100), 2)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["client"] = ClientSerializer(instance.client).data
        rep["branch"] = ClientBranchesSerializer(instance.branch).data
        rep["whouse"] = {"id": instance.whouse.id, "name": instance.whouse.name}
        return rep


class RejectOrderItemSerializer(serializers.Serializer):
    order_item_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)


class RejectOrderSerializer(serializers.Serializer):
    order_items = RejectOrderItemSerializer(many=True, required=True)
    rejector_role = serializers.ChoiceField(
        choices=["CLIENT", "OPERATOR", "MANAGER"], required=True
    )
    
    class Meta:
        ref_name = 'orders_reject_order'


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
            "payment_status",
            "order_type",
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

        items_text = _format_order_items_for_sms(order)
        sms_message = "Уважаемый клиент, ваш заказ №{id} был успешно оформлен.".format(
            id=order.display_id
        )
        if items_text:
            sms_message += "\n\nСостав заказа:\n{items}".format(items=items_text)
        order.client.send_sms(
            sms_message
        )
    

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
                    OrderItem.objects.filter(id=item_id, order=instance).update(
                        **item_data
                    )
                else:
                    OrderItem.objects.create(order=instance, **item_data)

        if sub_orders_data is not None:
            incoming_ids = {sub["id"] for sub in sub_orders_data if "id" in sub}
            instance.sub_orders.exclude(id__in=incoming_ids).delete()
            for sub_data in sub_orders_data:
                sub_order_items_data = sub_data.pop("sub_order_items", None)
                sub_id = sub_data.pop("id", None)
                if sub_id:
                    SubOrder.objects.filter(id=sub_id, order=instance).update(
                        **sub_data
                    )
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

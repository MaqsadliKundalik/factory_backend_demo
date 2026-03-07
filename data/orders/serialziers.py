from rest_framework import serializers
from .models import Order, SubOrder
from data.products.serializers import ProductSerializer, ProductTypeSerializer, ProductUnitSerializer
from data.clients.serializers import ClientSerializer, ClientBranchesSerializer
from apps.drivers.serializers import DriverSerializer
from data.transports.serializers import TransportSerializer
from data.filedatas.serializers import FileSerializer

class ExternalDriverSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=20)
    car_number = serializers.CharField(max_length=20)

class StatusHistorySerializer(serializers.Serializer):
    status = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()


class SubOrderSerializer(serializers.ModelSerializer):
    status_history = serializers.ListField(child=serializers.JSONField(), required=False)
    files = FileSerializer(many=True, required=False)
    class Meta:
        model = SubOrder
        fields = ['id', 'order', 'driver', 'transport', 'quantity', 'files', 'status', 'status_history']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["order"] = OrderSerializer(instance.order).data if instance.order else None
        repr['driver'] = DriverSerializer(instance.driver).data
        repr['transport'] = TransportSerializer(instance.transport).data
        repr['files'] = FileSerializer(instance.files, many=True).data
        return repr

class OrderSerializer(serializers.ModelSerializer):
    external_drivers = serializers.ListField(child=serializers.JSONField(), required=False)
    sub_orders = SubOrderSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'client', 'branch', 'whouse', 'product', 'type', 'unit', 'status', 'external_drivers', "sub_orders"]
        read_only_fields = ['id']
        

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['client'] = ClientSerializer(instance.client).data
        repr['branch'] = ClientBranchesSerializer(instance.branch).data
        repr['whouse'] = {
            'id': instance.whouse.id,
            'name': instance.whouse.name
        }
        repr['product'] = ProductSerializer(instance.product).data
        repr['type'] = ProductTypeSerializer(instance.type).data
        repr['unit'] = ProductUnitSerializer(instance.unit).data
        repr['sub_orders'] = SubOrderSerializer(instance.sub_orders, many=True).data
        return repr


class OrderStatusHistorySerizalizer(serializers.Serializer):
    status = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()

class OrderAndSubOrderCreateSerializer(serializers.ModelSerializer):
    external_drivers = serializers.ListField(child=serializers.JSONField(), required=False)
    sub_orders = SubOrderSerializer(many=True, required=True)
    class Meta:
        model = Order
        fields = ['id', 'client', 'branch', 'whouse', 'product', 'type', 'unit', 'status', 'external_drivers', "sub_orders"]
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['client'] = ClientSerializer(instance.client).data
        repr['branch'] = ClientBranchesSerializer(instance.branch).data
        repr['whouse'] = {
            'id': instance.whouse.id,
            'name': instance.whouse.name
        }
        repr['product'] = ProductSerializer(instance.product).data
        repr['type'] = ProductTypeSerializer(instance.type).data
        repr['unit'] = ProductUnitSerializer(instance.unit).data
        repr['sub_orders'] = SubOrderSerializer(instance.sub_orders, many=True).data
        return repr

    def create(self, validated_data):
        sub_orders = validated_data.pop('sub_orders')
        order = Order.objects.create(**validated_data)
        for sub_order in sub_orders:
            SubOrder.objects.create(order=order, **sub_order)
        return order
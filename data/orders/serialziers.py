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

class OrderSerializer(serializers.ModelSerializer):
    external_drivers = ExternalDriverSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'client', 'branch', 'whouse', 'product', 'type', 'unit', 'status', 'external_drivers']
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
        return repr

class SubOrderSerializer(serializers.ModelSerializer):
    status_history = StatusHistorySerializer(many=True, required=False)
    files = FileSerializer(many=True, required=False)
    class Meta:
        model = SubOrder
        fields = ['id', 'order', 'driver', 'transport', 'quantity', 'files', 'status', 'status_history']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['driver'] = DriverSerializer(instance.driver).data
        repr['transport'] = TransportSerializer(instance.transport).data
        repr['files'] = FileSerializer(instance.files, many=True).data
        return repr

class OrderStatusHistorySerizalizer(serializers.Serializer):
    status = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField()
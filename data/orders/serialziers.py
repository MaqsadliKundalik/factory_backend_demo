from rest_framework import serializers
from .models import Order, SubOrder
from data.products.serializers import ProductSerializer, ProductTypeSerializer, ProductUnitSerializer
from data.clients.serializers import ClientSerializer, ClientBranchesSerializer
from data.whouse.serializers import WhouseSerializer
from apps.drivers.serializers import DriverSerializer
from data.transports.serializers import TransportSerializer
from data.filedatas.serializers import FileSerializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'client', 'branch', 'whouse', 'product', 'type', 'unit', 'status']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['client'] = ClientSerializer(instance.client).data
        repr['branch'] = ClientBranchesSerializer(instance.branch).data
        repr['whouse'] = WhouseSerializer(instance.whouse).data
        repr['product'] = ProductSerializer(instance.product).data
        repr['type'] = ProductTypeSerializer(instance.type).data
        repr['unit'] = ProductUnitSerializer(instance.unit).data
        return repr

class SubOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubOrder
        fields = ['id', 'order', 'driver', 'transport', 'quantity', 'files', 'status']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['driver'] = DriverSerializer(instance.driver).data
        repr['transport'] = TransportSerializer(instance.transport).data
        repr['files'] = FileSerializer(instance.files, many=True).data
        return repr
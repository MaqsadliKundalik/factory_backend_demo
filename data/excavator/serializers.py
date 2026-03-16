from rest_framework import serializers
from .models import ExcavatorOrder, ExcavatorSubOrder
from data.filedatas.serializers import FileSerializer
from data.transports.serializers import TransportSerializer
from apps.drivers.serializers import DriverSerializer


class ExcavatorSubOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcavatorSubOrder
        fields = [
            'id', 'parent', 'driver',
            'start_date', 'end_date',
            'transport', 'status',
            'status_history',
            'before_sign', 'before_files',
            'after_sign', 'after_files',
            'created_at',
        ]
        read_only_fields = ['id', 'status_history', 'created_at', 'before_sign', 'before_files', 'after_sign', 'after_files']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['driver'] = DriverSerializer(instance.driver).data if instance.driver else None
        rep['transport'] = TransportSerializer(instance.transport).data if instance.transport else None
        rep['before_sign'] = FileSerializer(instance.before_sign).data if instance.before_sign else None
        rep['before_files'] = FileSerializer(instance.before_files.all(), many=True).data
        rep['after_sign'] = FileSerializer(instance.after_sign).data if instance.after_sign else None
        rep['after_files'] = FileSerializer(instance.after_files.all(), many=True).data
        return rep


class ExcavatorOrderSerializer(serializers.ModelSerializer):
    sub_orders = ExcavatorSubOrderSerializer(many=True, read_only=True)

    class Meta:
        model = ExcavatorOrder
        fields = [
            'id', 'display_id',
            'client_name', 'phone_number',
            'lat', 'lon', 'address',
            'start_date', 'end_date',
            'comment', 'status', 
            'payment_status', 'files',
            'sub_orders',
            'created_at',
        ]
        read_only_fields = ['id', 'display_id', 'created_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['files'] = FileSerializer(instance.files.all(), many=True).data
        return rep

class ExcavatorOrderCreateSerializer(serializers.ModelSerializer):
    sub_orders = ExcavatorSubOrderSerializer(many=True, required=False)

    class Meta:
        model = ExcavatorOrder
        fields = [
            'id', 'display_id',
            'client_name', 'phone_number',
            'lat', 'lon', 'address',
            'start_date', 'end_date',
            'comment', 'sub_orders',
        ]
        read_only_fields = ['id', 'display_id']

    def create(self, validated_data):
        sub_orders_data = validated_data.pop('sub_orders', [])
        order = ExcavatorOrder.objects.create(**validated_data)
        for sub_data in sub_orders_data:
            ExcavatorSubOrder.objects.create(parent=order, **sub_data)
        return order


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ExcavatorOrder.Status.choices)
    timestamp = serializers.DateTimeField()

class StartOrderSerializer(serializers.Serializer):
    sign = serializers.FileField(required=False)
    timestamp = serializers.DateTimeField()


class FinishOrderSerializer(serializers.Serializer):
    sign = serializers.FileField(required=False)
    timestamp = serializers.DateTimeField()


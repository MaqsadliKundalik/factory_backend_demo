from rest_framework import serializers
from .models import ExcavatorOrder, ExcavatorSubOrder
from data.files.serializers import FileSerializer
from data.transports.serializers import TransportSerializer
from data.transports.models import Transport
from data.drivers.serializers import DriverSerializer
from data.drivers.models import Driver


class ExcavatorSubOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcavatorSubOrder
        fields = [
            "id",
            "parent",
            "driver",
            "transport",
            "status",
            "status_history",
            "before_sign",
            "before_files",
            "after_sign",
            "after_files",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status_history",
            "created_at",
            "before_sign",
            "before_files",
            "after_sign",
            "after_files",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["parent"] = {
            "id": instance.parent.id,
            "display_id": instance.parent.display_id,
            "client_name": instance.parent.client_name,
            "phone_number": instance.parent.phone_number,
            "lat": instance.parent.lat,
            "lon": instance.parent.lon,
            "address": instance.parent.address,
            "start_date": instance.parent.start_date,
            "end_date": instance.parent.end_date,
            "comment": instance.parent.comment,
            "whouse": (
                {"id": instance.parent.whouse.id, "name": instance.parent.whouse.name}
                if instance.parent.whouse
                else None
            ),
            "payment_status": instance.parent.payment_status,
            "status": instance.parent.status,
            "files": FileSerializer(instance.parent.files.all(), many=True).data,
            "created_at": instance.parent.created_at,
        }
        rep["driver"] = (
            DriverSerializer(instance.driver).data if instance.driver else None
        )
        rep["transport"] = (
            TransportSerializer(instance.transport).data if instance.transport else None
        )
        rep["before_sign"] = (
            FileSerializer(instance.before_sign).data if instance.before_sign else None
        )
        rep["before_files"] = FileSerializer(
            instance.before_files.all(), many=True
        ).data
        rep["after_sign"] = (
            FileSerializer(instance.after_sign).data if instance.after_sign else None
        )
        rep["after_files"] = FileSerializer(instance.after_files.all(), many=True).data
        return rep


class ExcavatorOrderSerializer(serializers.ModelSerializer):
    sub_orders = ExcavatorSubOrderSerializer(many=True, read_only=True)

    class Meta:
        model = ExcavatorOrder
        fields = [
            "id",
            "display_id",
            "client_name",
            "phone_number",
            "lat",
            "lon",
            "address",
            "start_date",
            "end_date",
            "comment",
            "status",
            "payment_status",
            "files",
            "start_date",
            "end_date",
            "sub_orders",
            "created_at",
            "whouse",
        ]
        read_only_fields = ["id", "display_id", "created_at"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["files"] = (FileSerializer(instance.files.all(), many=True).data,)
        rep["whouse"] = (
            {"id": instance.whouse.id, "name": instance.whouse.name}
            if instance.whouse
            else None
        )
        return rep


class ExcavatorSubOrderCreateSerializer(serializers.Serializer):
    driver = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(), required=True
    )
    transport = serializers.PrimaryKeyRelatedField(
        queryset=Transport.objects.all(), required=True
    )


class ExcavatorOrderCreateSerializer(serializers.ModelSerializer):
    sub_orders = ExcavatorSubOrderCreateSerializer(many=True, required=False)

    class Meta:
        model = ExcavatorOrder
        fields = [
            "id",
            "display_id",
            "client_name",
            "phone_number",
            "lat",
            "lon",
            "address",
            "whouse",
            "start_date",
            "end_date",
            "comment",
            "sub_orders",
        ]
        read_only_fields = ["id", "display_id", "start_date", "end_date"]

    def create(self, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", [])
        order = ExcavatorOrder.objects.create(**validated_data)
        for sub_data in sub_orders_data:
            ExcavatorSubOrder.objects.create(parent=order, **sub_data)
        return order


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ExcavatorOrder.Status.choices)
    timestamp = serializers.DateTimeField()


class StartOrderSerializer(serializers.Serializer):
    sign = serializers.UUIDField(required=False)
    files = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    timestamp = serializers.DateTimeField()


class FinishOrderSerializer(serializers.Serializer):
    sign = serializers.UUIDField(required=False)
    files = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    timestamp = serializers.DateTimeField()

from rest_framework import serializers

from data.orders.serialziers import StatusHistorySerializer
from .models import ExcavatorOrder, ExcavatorSubOrder
from data.files.serializers import FileSerializer
from data.transports.serializers import TransportSerializer
from data.transports.models import Transport
from data.drivers.serializers import DriverSerializer
from data.drivers.models import Driver
from datetime import datetime
from django.utils import timezone

def calculate_total_time(instance):
    
    history = instance.status_history or []
    total_seconds = 0
    
    for i, entry in enumerate(history):
        if not isinstance(entry, dict):
            continue
        if i + 1 >= len(history):
            continue
        next_entry = history[i + 1]
        if not isinstance(next_entry, dict):
            continue
        try:
            t1 = datetime.fromisoformat(str(entry.get("changed_at") or entry.get("timestamp")))
            t2 = datetime.fromisoformat(str(next_entry.get("changed_at") or next_entry.get("timestamp")))
            
            if t1.tzinfo is None:
                t1 = timezone.make_aware(t1)
            if t2.tzinfo is None:
                t2 = timezone.make_aware(t2)
            
            seconds = (t2 - t1).total_seconds()
            if seconds >= 0:
                total_seconds += seconds
        except (KeyError, ValueError, TypeError):
            continue
    
    if total_seconds > 0:
        return "%02d:%02d:%02d" % (total_seconds // 3600, (total_seconds % 3600) // 60, total_seconds % 60)
        
    return None

class ExcavatorSubOrderSerializer(serializers.ModelSerializer):
    total_time = serializers.SerializerMethodField()
    
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
            "total_time",
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
            "total_time",
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
        rep["total_time"] = calculate_total_time(instance)

        return rep

class ExcavatorSubOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcavatorSubOrder
        fields = [
            "id",
            "parent",
            "status",
            "before_sign",
            "before_files",
            "after_sign",
            "after_files",
            "status_history",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "before_sign",
            "before_files",
            "after_sign",
            "after_files",
            "status_history",
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
            "rejector_role",
            "rejector_id",
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
        rep["sub_orders"] = ExcavatorSubOrderSerializer(
            instance.sub_orders, many=True
        ).data
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
            "payment_status",
            "lat",
            "lon",
            "address",
            "whouse",
            "start_date",
            "end_date",
            "comment",
            "files",
            "sub_orders",
        ]
        read_only_fields = ["id", "display_id"]

    def create(self, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", [])
        files_data = validated_data.pop("files", [])
        order = ExcavatorOrder.objects.create(**validated_data)
        if files_data:
            order.files.set(files_data)
        for sub_data in sub_orders_data:
            ExcavatorSubOrder.objects.create(parent=order, **sub_data)
        return order

    def update(self, instance, validated_data):
        sub_orders_data = validated_data.pop("sub_orders", None)
        files_data = validated_data.pop("files", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if files_data is not None:
            instance.files.set(files_data)

        if sub_orders_data is not None:
            instance.sub_orders.all().delete()
            for sub_data in sub_orders_data:
                ExcavatorSubOrder.objects.create(parent=instance, **sub_data)

        return instance


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

class RejectOrderSerializer(serializers.Serializer):    
    rejector_role = serializers.ChoiceField(choices=ExcavatorOrder.Rejector.choices)
    rejector_id = serializers.UUIDField()
    
    class Meta:
        ref_name = 'excavator_reject_order'
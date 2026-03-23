from rest_framework import serializers
from .models import Transport
from typing import TYPE_CHECKING
from data.orders.models import SubOrder


class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ["id", "name", "type", "car_type", "number", "whouse", "created_at"]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["whouse"] = {
            "id": instance.whouse.id,
            "name": instance.whouse.name,
        }
        exists: bool = instance.sub_orders.filter(
            status__in=[
                SubOrder.Status.NEW,
                SubOrder.Status.IN_PROGRESS,
                SubOrder.Status.ARRIVED,
                SubOrder.Status.ON_WAY,
                SubOrder.Status.UNLOADING,
            ]
        ).exists()
        representation["has_suborder"] = exists

        return representation


class SelectTransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ["id", "name", "number", "car_type"]

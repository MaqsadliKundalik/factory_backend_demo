from rest_framework import serializers
from .models import Notification
from data.orders.serialziers import SubOrderListSerializer
from data.excavator.serializers import ExcavatorSubOrderListSerializer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "from_role",
            "to_role",
            "to_user_id",
            "is_read",
            "target_type",
            "order_obj",
            "excavator_obj",
            
        ]
        read_only_fields = ["id"]

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            if instance.order_obj:
                representation["order_obj"] = SubOrderListSerializer(instance.order_obj).data
            if instance.excavator_obj:
                representation["excavator_obj"] = ExcavatorSubOrderListSerializer(instance.excavator_obj).data
            return representation
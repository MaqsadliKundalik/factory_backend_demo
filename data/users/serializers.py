from rest_framework import serializers
from apps.drivers.models import Driver
from apps.guard.models import Guard
from apps.factory_operator.models import FactoryOperator
from apps.whouse_manager.models import WhouseManager

class UnifiedUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    phone_number = serializers.CharField()
    role = serializers.SerializerMethodField()
    whouses = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_role(self, obj):
        if isinstance(obj, WhouseManager):
            return "manager"
        elif isinstance(obj, FactoryOperator):
            return "operator"
        elif isinstance(obj, Driver):
            return "driver"
        elif isinstance(obj, Guard):
            return "guard"
        return "unknown"

    def get_whouses(self, obj):
        if isinstance(obj, WhouseManager):
            return [str(w.id) for w in obj.whouses.all()]
        elif hasattr(obj, 'whouse') and obj.whouse:
            return [str(obj.whouse.id)]
        return []
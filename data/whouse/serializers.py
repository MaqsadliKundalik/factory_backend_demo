from rest_framework import serializers
from .models import Whouse
from apps.whouse_manager.serializers.whouse_manager import WhouseManagerSerializer
from apps.factory_operator.serializers.factory_operator import FactoryOperatorSerializer
from apps.drivers.serializers import DriverSerializer
from apps.guard.serializers import GuardSerializer

class WhouseGetSerializer(serializers.ModelSerializer):
    managers = WhouseManagerSerializer(many=True, read_only=True)
    factory_operators = FactoryOperatorSerializer(many=True, read_only=True)
    drivers = DriverSerializer(many=True, read_only=True)
    guards = GuardSerializer(many=True, read_only=True)

    class Meta:
        model = Whouse
        fields = ["id", "name", "managers", "factory_operators", "drivers", "guards"]

class WhouseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whouse
        fields = ["id", "name"]

from rest_framework import serializers
from apps.whouse.models import Whouse
from apps.whouse_manager.serializers.whouse_manager import WhouseManagerSerializer
from apps.factory_operator.serializers.factory_operator import FactoryOperatorSerializer

class WhouseGetSerializer(serializers.ModelSerializer):
    whouse_managers = WhouseManagerSerializer(many=True)
    factory_operators = FactoryOperatorSerializer(many=True)

    class Meta:
        model = Whouse
        fields = ["id", "name", "whouse_managers", "factory_operators"]

class WhouseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whouse
        fields = ["id", "name"]

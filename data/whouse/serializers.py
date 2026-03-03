from rest_framework import serializers
from .models import Whouse
from data.users.models import FactoryUser
from apps.drivers.serializers import DriverSerializer
from apps.whouse_manager.serializers.whouse_manager import WhouseManagerSerializer
from apps.factory_operator.serializers.factory_operator import FactoryOperatorSerializer
from apps.guard.serializers import GuardSerializer

class WhouseGetSerializer(serializers.ModelSerializer):
    managers = serializers.SerializerMethodField()
    factory_operators = serializers.SerializerMethodField()
    drivers = serializers.SerializerMethodField()
    guards = serializers.SerializerMethodField()

    class Meta:
        model = Whouse
        fields = ["id", "name", "managers", "factory_operators", "drivers", "guards"]

    def get_managers(self, obj):
        users = FactoryUser.objects.filter(whouses=obj, role='manager')
        return WhouseManagerSerializer(users, many=True).data

    def get_factory_operators(self, obj):
        users = FactoryUser.objects.filter(whouses=obj, role='operator')
        return FactoryOperatorSerializer(users, many=True).data

    def get_drivers(self, obj):
        from apps.drivers.models import Driver
        drivers = Driver.objects.filter(whouse=obj)
        return DriverSerializer(drivers, many=True).data

    def get_guards(self, obj):
        users = FactoryUser.objects.filter(whouses=obj, role='guard')
        return GuardSerializer(users, many=True).data

class WhouseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Whouse
        fields = ["id", "name"]

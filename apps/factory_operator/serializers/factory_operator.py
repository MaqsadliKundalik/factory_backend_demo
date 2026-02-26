from rest_framework import serializers
from apps.factory_operator.models import FactoryOperator

class FactoryOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryOperator
        fields = ["id", "name", "phone_number", "whouse"]
        ref_name = "FactoryOperator"
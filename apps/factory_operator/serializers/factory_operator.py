from rest_framework import serializers
from data.users.models import FactoryUser

class FactoryOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryUser
        fields = ["id", "name", "phone_number", "whouses"]
        ref_name = "FactoryOperator"
from rest_framework import serializers
from data.users.models import FactoryUser

class WhouseManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryUser
        fields = ["id", "name", "phone_number", "password", "whouse"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        validated_data['role'] = 'manager'
        password = validated_data.pop('password')
        manager = FactoryUser(**validated_data)
        manager.set_password(password)
        manager.save()
        return manager

from rest_framework import serializers
from data.users.models import FactoryUser

class WhouseManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryUser
        fields = ["id", "name", "phone_number", "password", "whouses"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        validated_data['role'] = 'manager'
        password = validated_data.pop('password')
        whouses = validated_data.pop('whouses', [])
        manager = FactoryUser.objects.create(**validated_data)
        manager.set_password(password)
        manager.whouses.set(whouses)
        manager.save()
        return manager

from rest_framework import serializers
from apps.whouse_manager.models import WhouseManager

class WhouseManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhouseManager
        fields = ["id", "name", "phone_number", "password", "whouses"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        manager = WhouseManager(**validated_data)
        manager.set_password(password)
        manager.save()
        return manager

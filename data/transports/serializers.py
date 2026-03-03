from rest_framework import serializers
from .models import Transport

class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ['id', 'name', 'type', 'number', 'whouse']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['whouse'] = {
            'id': instance.whouse.id,
            'name': instance.whouse.name
        }
        return representation
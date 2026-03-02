from rest_framework import serializers
from .models import Transport

class TransportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transport
        fields = ['id', 'name', 'type', 'number', 'place', 'whouse']
        read_only_fields = ['id']
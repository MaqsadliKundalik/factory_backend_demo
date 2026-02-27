from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'inn_number', 'phone_number', 'latitude', 'longitude', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
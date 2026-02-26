from rest_framework import serializers
from .models import ProductType

class ProductTypeSerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ProductType
        fields = [
            'id', 'name', 'types', 'unities', 'whouse',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
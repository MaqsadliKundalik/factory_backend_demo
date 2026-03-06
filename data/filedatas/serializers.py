from rest_framework import serializers
from .models import File
from app.settings import BASE_URL

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['file'] = f"{BASE_URL}{instance.file.url}" if instance.file else None
        return representation

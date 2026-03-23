from rest_framework import serializers
from .models import File, Documents
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

class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields = ['id', 'file', "type", "object_id", 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['file'] = FileSerializer(instance.file).data if instance.file else None
        return representation

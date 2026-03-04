from rest_framework import serializers
from .models import Client, ClientBranches
from data.filedatas.serializers import FileSerializer
from app.settings import BASE_URL

class ClientBranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientBranches
        fields = ['id', 'client', 'name', 'address', 'longitude', 'latitude']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'client': {'read_only': False, 'required': False}
        }

class ClientBranchesBulkSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)

class ClientSerializer(serializers.ModelSerializer):
    branches = ClientBranchesSerializer(many=True, read_only=True)
    class Meta:
        model = Client
        fields = ['id', 'name', 'inn_number', 'phone_number', 'branches', 'photo']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = {
            "id": instance.photo.id,
            "file": BASE_URL + instance.photo.file.url
        } if instance.photo else None
        representation['branches'] = ClientBranchesSerializer(instance.branches, many=True).data
        representation['whouse'] = {
            "id": instance.whouse.id,
            "name": instance.whouse.name
        }
        return representation

class ClientAndBranchesBulkSerializer(serializers.ModelSerializer):    
    branches = ClientBranchesBulkSerializer(many=True, required=False)
    class Meta:
        model = Client
        fields = ['id', 'name', 'inn_number', 'phone_number', 'photo', 'whouse', 'branches']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'whouse': {'required': False}
        }

    def create(self, validated_data):
        branches_data = validated_data.pop('branches', [])
        
        # Handle whouse fallback
        if not validated_data.get('whouse'):
            user = self.context['request'].user
            whouse = user.whouses.first()
            if whouse:
                validated_data['whouse'] = whouse
        
        client = Client.objects.create(**validated_data)
        
        for branch_item in branches_data:
            ClientBranches.objects.create(client=client, **branch_item)
            
        return client

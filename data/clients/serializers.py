from rest_framework import serializers
from .models import Client, ClientBranches

class ClientBranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientBranches
        fields = ['id', 'client', 'name', 'address', 'longitude', 'latitude']
        read_only_fields = ['id']

class ClientSerializer(serializers.ModelSerializer):
    branches = ClientBranchesSerializer(many=True, read_only=True)
    class Meta:
        model = Client
        fields = ['id', 'name', 'inn_number', 'phone_number', 'branches']
        read_only_fields = ['id']

from rest_framework import serializers
from .models import Client, ClientBranches, ClientPhone
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

class ClientPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPhone
        fields = ['id', 'client', 'phone_number', 'name', 'role']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'client': {'read_only': False, 'required': False}
        }

class ClientSerializer(serializers.ModelSerializer):
    branches = ClientBranchesSerializer(many=True, read_only=True)
    phone_numbers = ClientPhoneSerializer(many=True, required=False)
    files = FileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'name', 'inn_number', 'branches', 'photo', 'phone_numbers', 'files']
        read_only_fields = ['id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = {
            "id": instance.photo.id,
            "file": BASE_URL + instance.photo.file.url
        } if instance.photo else None
        representation['branches'] = ClientBranchesSerializer(instance.branches, many=True).data
        representation['phone_numbers'] = ClientPhoneSerializer(instance.phones.all(), many=True).data
        representation['files'] = FileSerializer(instance.files.all(), many=True).data
        representation['whouse'] = {
            "id": instance.whouse.id,
            "name": instance.whouse.name
        }
        return representation

    def update(self, instance, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', None)
        
        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update phone numbers
        if phone_numbers_data is not None:
            instance.phones.all().delete()
            for phone_item in phone_numbers_data:
                # client field ni olib tashlash kerak, chunki u validated_data da bor
                phone_data = {k: v for k, v in phone_item.items() if k != 'client'}
                ClientPhone.objects.create(client=instance, **phone_data)
        
        return instance

class ClientAndBranchesBulkSerializer(serializers.ModelSerializer):    
    branches = ClientBranchesBulkSerializer(many=True, required=False)
    phone_numbers = ClientPhoneSerializer(many=True, required=False)
    files = serializers.ListField(child=serializers.UUIDField(), required=False)
    class Meta:
        model = Client
        fields = ['id', 'name', 'inn_number', 'phone_numbers', 'photo', 'whouse', 'branches', 'files']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'whouse': {'required': False}
        }

    def create(self, validated_data):
        branches_data = validated_data.pop('branches', [])
        phone_numbers_data = validated_data.pop('phone_numbers', [])
        files_data = validated_data.pop('files', [])
        
        # Handle whouse fallback
        if not validated_data.get('whouse'):
            user = self.context['request'].user
            whouse = user.whouses.first()
            if whouse:
                validated_data['whouse'] = whouse
        
        client = Client.objects.create(**validated_data)
        
        for branch_item in branches_data:
            ClientBranches.objects.create(client=client, **branch_item)
        
        for phone_number_item in phone_numbers_data:
            ClientPhone.objects.create(client=client, **phone_number_item)
        
        # Handle files
        if files_data:
            from data.filedatas.models import File
            files = File.objects.filter(id__in=files_data)
            client.files.set(files)
            
        return client

    def update(self, instance, validated_data):
        branches_data = validated_data.pop('branches', None)
        phone_numbers_data = validated_data.pop('phone_numbers', None)
        files_data = validated_data.pop('files', None)
        
        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update branches
        if branches_data is not None:
            instance.branches.all().delete()
            for branch_item in branches_data:
                ClientBranches.objects.create(client=instance, **branch_item)
        
        # Update phone numbers
        if phone_numbers_data is not None:
            instance.phones.all().delete()
            for phone_item in phone_numbers_data:
                ClientPhone.objects.create(client=instance, **phone_item)
        
        # Update files
        if files_data is not None:
            from data.filedatas.models import File
            files = File.objects.filter(id__in=files_data)
            instance.files.set(files)
        return instance

class SelectClientSerializer(serializers.ModelSerializer):
    branches = ClientBranchesSerializer(many=True, read_only=True)
    phone_numbers = ClientPhoneSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    class Meta:
        model = Client
        fields = ['id', 'name', "photo", "branches", "phone_numbers", "files"]

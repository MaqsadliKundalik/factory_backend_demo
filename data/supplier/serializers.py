from rest_framework import serializers
from .models import Supplier, SupplierPhone
from data.filedatas.serializers import FileSerializer
from app.settings import BASE_URL

class SupplierPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierPhone
        fields = ['id', 'supplier', 'phone_number', 'name', 'role']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'supplier': {'read_only': False, 'required': False}
        }

class SupplierPhoneBulkSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)

class SupplierSerializer(serializers.ModelSerializer):
    phone_numbers = SupplierPhoneSerializer(many=True, required=False)
    files = FileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'inn_number', 'photo', 'phone_numbers', 'files', "created_at"]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = FileSerializer(instance.photo).data if instance.photo else None
        representation['phone_numbers'] = SupplierPhoneSerializer(instance.phones.all(), many=True).data
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
                phone_data = {k: v for k, v in phone_item.items() if k != 'supplier'}
                SupplierPhone.objects.create(supplier=instance, **phone_data)
        
        return instance

class SupplierBulkSerializer(serializers.ModelSerializer):    
    phone_numbers = SupplierPhoneSerializer(many=True, required=False)
    files = serializers.ListField(child=serializers.UUIDField(), required=False)
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'inn_number', 'phone_numbers', 'photo', 'whouse', 'files']
        extra_kwargs = {
            'id': {'read_only': False, 'required': False},
            'whouse': {'required': False}
        }

    def create(self, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', [])
        files_data = validated_data.pop('files', [])
        
        # Handle whouse fallback
        if not validated_data.get('whouse'):
            user = self.context['request'].user
            whouse = user.whouses.first()
            if whouse:
                validated_data['whouse'] = whouse
        
        supplier = Supplier.objects.create(**validated_data)
                
        for phone_number_item in phone_numbers_data:
            SupplierPhone.objects.create(supplier=supplier, **phone_number_item)
        
        # Handle files
        if files_data:
            from data.filedatas.models import File
            files = File.objects.filter(id__in=files_data)
            supplier.files.set(files)
            
        return supplier

    def update(self, instance, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', None)
        files_data = validated_data.pop('files', None)
        
        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update phone numbers
        if phone_numbers_data is not None:
            instance.phones.all().delete()
            for phone_number_item in phone_numbers_data:
                SupplierPhone.objects.create(supplier=instance, **phone_number_item)
        
        # Update files
        if files_data is not None:
            from data.filedatas.models import File
            files = File.objects.filter(id__in=files_data)
            instance.files.set(files)
        return instance

class SelectSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', "photo"]

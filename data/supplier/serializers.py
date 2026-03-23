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
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'inn_number', 'photo', "type", 'phone_numbers', "created_at"]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = FileSerializer(instance.photo).data if instance.photo else None
        representation['phone_numbers'] = SupplierPhoneSerializer(instance.phones.all(), many=True).data
        representation['whouse'] = {
            "id": instance.whouse.id,
            "name": instance.whouse.name
        }
        return representation

    def validate(self, attrs):
        if attrs.get('type') == 'internal':
            if not attrs.get('inn_number'):
                raise serializers.ValidationError({'inn_number': 'Internal uchun majburiy.'})
            if not attrs.get('whouse'):
                raise serializers.ValidationError({'whouse': 'Internal uchun majburiy.'})
        return attrs


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
    phone_numbers = SupplierPhoneBulkSerializer(many=True, required=False)
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'inn_number', 'phone_numbers', 'photo', 'whouse', 'type']
        extra_kwargs = {
            'whouse': {'required': False}
        }
        read_only_fields = ['id']


    def validate(self, attrs):
        if attrs.get('type') == 'internal':
            if not attrs.get('inn_number'):
                raise serializers.ValidationError({'inn_number': 'Internal uchun majburiy.'})
            if not attrs.get('whouse'):
                raise serializers.ValidationError({'whouse': 'Internal uchun majburiy.'})
        return attrs


    def create(self, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', [])
        
        # Handle whouse fallback
        if not validated_data.get('whouse'):
            user = self.context['request'].user
            whouse = user.whouses.first()
            if whouse:
                validated_data['whouse'] = whouse
        
        supplier = Supplier.objects.create(**validated_data)
                
        for phone_number_item in phone_numbers_data:
            SupplierPhone.objects.create(supplier=supplier, **phone_number_item)
                
        return supplier

    def update(self, instance, validated_data):
        phone_numbers_data = validated_data.pop('phone_numbers', None)
        
        # Update client fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update phone numbers
        if phone_numbers_data is not None:
            instance.phones.all().delete()
            for phone_number_item in phone_numbers_data:
                SupplierPhone.objects.create(supplier=instance, **phone_number_item)
        
        return instance

class SelectSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', "photo", "type"]

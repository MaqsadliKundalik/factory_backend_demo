from rest_framework import serializers
from data.whouse.models import Whouse
from data.users.models import FactoryUser
import re
from data.files.serializers import FileSerializer

class FactoryUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FactoryUser
        fields = [
            'id', 'name', 'phone_number', 'password', 'role',
            'MAIN_PAGE', 'PRODUCTS_PAGE', 'ORDERS_PAGE', 'TRANSPORTS_PAGE', "created_at", "SUPPLIERS_PAGE", "EXCAVATORS_PAGE",
            'CLIENTS_PAGE', 'USERS_PAGE', 'READY_PRODUCTS_PAGE', 'DRIVERS_PAGE', 'WHEREHOUSES_PAGE', 'whouses', 'photo'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
        read_only_fields = ['id', 'created_at']


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['whouses'] = [{"id": whouse.id, "name": whouse.name} for whouse in instance.whouses.all()]
        representation['photo'] = FileSerializer(instance.photo).data if instance.photo else None
        return representation

    def validate_phone_number(self, value):
        if not re.match(r'^\+998\d{9}$', value):
            raise serializers.ValidationError("Номер телефона должен быть в формате +998XXXXXXXXX.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Phone number unique tekshiruvi
        phone_number = validated_data.get('phone_number')
        # FactoryUser da tekshirish (unique=True bor, lekin qo'shimcha tekshiruv)
        if FactoryUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon ro'yxatdan o'tgan"})
        
        # Driver da tekshirish
        from data.drivers.models import Driver
        if Driver.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon haydovchi tomonidan ro'yxatdan o'tgan"})
        
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Phone number unique tekshiruvi (agar o'zgartirilayotgan bo'lsa)
        if 'phone_number' in validated_data:
            new_phone_number = validated_data['phone_number']
            # FactoryUser lar orasida tekshirish
            if FactoryUser.objects.filter(phone_number=new_phone_number).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon boshqa foydalanuvchi tomonidan ro'yxatdan o'tgan"})
            
            # Driver lar orasida tekshirish
            from data.drivers.models import Driver
            if Driver.objects.filter(phone_number=new_phone_number).exists():
                raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon haydovchi tomonidan ro'yxatdan o'tgan"})
        
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class FactoryUserResetpasswordSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

# For backward compatibility if needed, but pointing to FactoryUser
class UnifiedUserSerializer(FactoryUserSerializer):
    pass

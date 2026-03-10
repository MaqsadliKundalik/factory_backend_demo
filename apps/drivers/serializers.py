from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.drivers.models import Driver
from utils.password import password_validator
from data.filedatas.serializers import FileSerializer
from data.orders.models import SubOrder
from data.users.models import FactoryUser

class DriverSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+998\d{9}$",
                message="Invalid Uzbek phone number. Format: +998XXXXXXXXX",
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        validators=[password_validator(8)]
    )

    class Meta:
        model = Driver
        fields = [
            "id", "name", "phone_number", "password", "photo", "files", "whouse", "created_at"
        ]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = FileSerializer(instance.photo).data if instance.photo else None
        representation['files'] = FileSerializer(instance.files, many=True).data if instance.files else None
        representation['whouse'] = {
            "id": instance.whouse.id,
            "name": instance.whouse.name
        } if instance.whouse else None
        has_suborder: bool = instance.suborders.filter(status__in=[
            SubOrder.Status.NEW, 
            SubOrder.Status.IN_PROGRESS, 
            SubOrder.Status.ARRIVED,
            SubOrder.Status.ON_WAY,
            SubOrder.Status.UNLOADING
        ]).exists()
        representation['has_suborder'] = has_suborder
        return representation

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        phone_number = validated_data.get('phone_number')
        if Driver.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon ro'yxatdan o'tgan"})
        
        if FactoryUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon ro'yxatdan o'tgan"})
        
        driver = Driver.objects.create(
            PRODUCTS_PAGE=True,
            ORDERS_PAGE=True,
            TRANSPORTS_PAGE=True,
            **validated_data)
        if files:
            driver.files.set(files)
        return driver

    def update(self, instance, validated_data):
        files = validated_data.pop('files', None)
        
        if 'phone_number' in validated_data:
            new_phone_number = validated_data['phone_number']
            if Driver.objects.filter(phone_number=new_phone_number).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon boshqa haydovchi tomonidan ro'yxatdan o'tgan"})
            
            if FactoryUser.objects.filter(phone_number=new_phone_number).exists():
                raise serializers.ValidationError({"phone_number": "Bu telefon raqami allaqachon foydalanuvchi tomonidan ro'yxatdan o'tgan"})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if files is not None:
            instance.files.set(files)
            
        return instance


class DriverPasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        validators=[password_validator(8)]
    )
    
    def save(self):
        driver = self.context['driver']
        driver.set_password(self.validated_data['new_password'])
        driver.save()
        return driver

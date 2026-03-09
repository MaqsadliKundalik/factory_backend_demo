from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.drivers.models import Driver
from utils.password import password_validator
from data.filedatas.serializers import FileSerializer
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
            "id", "name", "phone_number", "password", "photo", "files", "whouse"
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['photo'] = FileSerializer(instance.photo).data if instance.photo else None
        representation['files'] = FileSerializer(instance.files, many=True).data if instance.files else None
        representation['whouse'] = {
            "id": instance.whouse.id,
            "name": instance.whouse.name
        } if instance.whouse else None
        return representation

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        driver = Driver.objects.create(
            PRODUCTS_PAGE=True,
            ORDERS_PAGE=True,
            TRANSPORTS_PAGE=True,
            **validated_data)
        driver.files.set(files)
        return driver

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
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

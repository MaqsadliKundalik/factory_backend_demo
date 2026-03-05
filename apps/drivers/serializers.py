from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.drivers.models import Driver
from utils.password import password_validator

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
        fields = ["id", "name", "phone_number", "password", "car_type", "car_number"]

    def create(self, validated_data):
        return Driver.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

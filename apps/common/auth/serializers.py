from rest_framework import serializers
from django.core.validators import RegexValidator
from utils.password import password_validator
from apps.whouse_manager.models import WhouseManager
from apps.factory_operator.models import FactoryOperator
from apps.drivers.models import Driver
from apps.guard.models import Guard

class UnifiedLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+998\d{9}$",
                message="Invalid Uzbek phone number. Format: +998XXXXXXXXX",
            )
        ]
    )
    password = serializers.CharField(validators=[password_validator(8)])

class WhouseManagerProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="manager", read_only=True)
    class Meta:
        model = WhouseManager
        fields = ["id", "name", "phone_number", "whouse", "role"]

class FactoryOperatorProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="operator", read_only=True)
    class Meta:
        model = FactoryOperator
        fields = ["id", "name", "phone_number", "whouse", "role"]

class DriverProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="driver", read_only=True)
    class Meta:
        model = Driver
        fields = ["id", "name", "phone_number", "whouse", "role"]

class GuardProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="guard", read_only=True)
    class Meta:
        model = Guard
        fields = ["id", "name", "phone_number", "whouse", "role"]

class UnifiedLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class UnifiedChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[password_validator(8)])

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        user = self.context.get("user")
        
        if not user or not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Eski parol noto'g'ri kiritildi."})

        return attrs

    def save(self, **kwargs):
        new_password = self.validated_data["new_password"]
        user = self.context.get("user")
        user.set_password(new_password)
        user.save()
        return user

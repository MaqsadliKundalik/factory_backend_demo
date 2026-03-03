from rest_framework import serializers
from django.core.validators import RegexValidator
from utils.password import password_validator
from data.users.models import FactoryUser
from apps.drivers.models import Driver

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

class FactoryUserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="user", read_only=True)
    class Meta:
        model = FactoryUser
        fields = ["id", "name", "phone_number", "role", "whouses", "crud_whouse_manager", "crud_factory_operator", "crud_driver", "crud_guard", "crud_product", "crud_transport", "crud_client", "read_whouse", "read_whouse_manager", "read_factory_operator", "read_driver", "read_guard", "read_product", "read_transport", "read_client"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['whouses'] = [{'id': wh.id, 'name': wh.name} for wh in instance.whouses.all()]
        return repr


class DriverProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="driver", read_only=True)
    class Meta:
        model = Driver
        fields = ["id", "name", "phone_number", "whouse", "role"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.whouse:
            repr['whouse'] = {'id': instance.whouse.id, 'name': instance.whouse.name}
        repr['permissions'] = None
        return repr

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

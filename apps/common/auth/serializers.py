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
                message="Недопустимый формат номера. Формат: +998XXXXXXXXX",
            )
        ]
    )
    password = serializers.CharField(validators=[password_validator(8)])

class FactoryUserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="user", read_only=True)
    class Meta:
        model = FactoryUser
        fields = ["id", "name", "phone_number", "role", "whouses", "MAIN_PAGE", "PRODUCTS_PAGE", "ORDERS_PAGE", "TRANSPORTS_PAGE", "WHEREHOUSES_PAGE", "CLIENTS_PAGE", "USERS_PAGE", "READY_PRODUCTS_PAGE", "DRIVERS_PAGE", "photo"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['whouses'] = [{'id': wh.id, 'name': wh.name} for wh in instance.whouses.all()]
        repr['photo'] = instance.photo.get_url() if instance.photo else None
        return repr


class DriverProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="driver", read_only=True)
    class Meta:
        model = Driver
        fields = ["id", "name", "phone_number", "whouse", "role", "photo"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.whouse:
            repr['whouse'] = {'id': instance.whouse.id, 'name': instance.whouse.name}   
        repr['photo'] = instance.photo.get_url() if instance.photo else None
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
            raise serializers.ValidationError({"old_password": "Неверный старый пароль."})

        return attrs

    def save(self, **kwargs):
        new_password = self.validated_data["new_password"]
        user = self.context.get("user")
        user.set_password(new_password)
        user.save()
        return user

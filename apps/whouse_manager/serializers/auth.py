import re
from typing import Dict
from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.whouse_manager.models import WhouseManager, WhouseManagerResetPasswordSession
from utils.password import password_validator

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+998\d{9}$",
                message="Invalid Uzbek phone number. Format: +998XXXXXXXXX",
            )
        ]
    )
    password = serializers.CharField(validators=[password_validator(8)])

    class Meta:
        ref_name = "WhouseManagerLogin"

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhouseManager
        fields = ["id", "name", "phone_number", "whouses"]
        ref_name = "WhouseManagerProfile"

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    class Meta:
        ref_name = "WhouseManagerLogout"

class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+998\d{9}$",
                message="Invalid Uzbek phone number. Format: +998XXXXXXXXX",
            )
        ]
    )

class ResetPasswordVerifiySerializer(serializers.Serializer):
    otp = serializers.IntegerField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[password_validator(8)])

    class Meta:
        ref_name = "WhouseManagerChangePassword"

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        manager: WhouseManager = self.context["whouse_manager"]

        if not manager.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Eski parol noto'g'ri kiritildi."})

        return attrs

    def save(self, **kwargs):
        new_password = self.validated_data["new_password"]
        manager: WhouseManager = self.context["whouse_manager"]

        manager.set_password(new_password)
        manager.save()

        return manager

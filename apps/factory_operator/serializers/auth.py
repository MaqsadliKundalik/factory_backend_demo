import re
from typing import Dict
from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.factory_operator.models import FactoryOperator, FactoryOperatorResetPasswordSession
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
        ref_name = "FactoryOperatorLogin"

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactoryOperator
        fields = ["id", "name", "phone_number", "whouses"]
        ref_name = "FactoryOperatorProfile"

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    class Meta:
        ref_name = "FactoryOperatorLogout"

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
        ref_name = "FactoryOperatorChangePassword"

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        operator: FactoryOperator = self.context["factory_operator"]

        if not operator.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Eski parol noto'g'ri kiritildi."})

        return attrs

    def save(self, **kwargs):
        new_password = self.validated_data["new_password"]
        operator: FactoryOperator = self.context["factory_operator"]

        operator.set_password(new_password)
        operator.save()

        return operator

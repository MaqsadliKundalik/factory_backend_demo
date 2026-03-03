from rest_framework import serializers
from django.core.validators import RegexValidator
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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        from apps.guard.models import Guard
        model = Guard
        fields = ["id", "name", "phone_number", "whouses"]

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[password_validator(8)])

    class Meta:
        ref_name = "GuardChangePassword"

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        from apps.guard.models import Guard
        guard: Guard = self.context["guard"]

        if not guard.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Eski parol noto'g'ri kiritildi."})

        return attrs

    def save(self, **kwargs):
        new_password = self.validated_data["new_password"]
        from apps.guard.models import Guard
        guard: Guard = self.context["guard"]

        guard.set_password(new_password)
        guard.save()

        return guard
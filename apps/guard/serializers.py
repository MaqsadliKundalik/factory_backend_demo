from rest_framework import serializers
from django.core.validators import RegexValidator
from apps.guard.models import Guard
from utils.password import password_validator

class GuardSerializer(serializers.ModelSerializer):
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
        model = Guard
        fields = ["id", "name", "phone_number", "password"]

    def create(self, validated_data):
        password = validated_data.pop('password')
        guard = Guard(**validated_data)
        guard.set_password(password)
        guard.save()
        return guard
from rest_framework import serializers
from data.whouse.models import Whouse
from data.users.models import FactoryUser
import re

class FactoryUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FactoryUser
        fields = [
            'id', 'name', 'phone_number', 'password', 'role',
            'MAIN_PAGE', 'PRODUCTS_PAGE', 'ORDERS_PAGE', 'TRANSPORTS_PAGE', 
            'CLIENTS_PAGE', 'USERS_PAGE', 'SETTINGS_PAGE', 'whouses'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
        read_only_fields = ['id']


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['whouses'] = [{"id": whouse.id, "name": whouse.name} for whouse in instance.whouses.all()]
        return representation

    def validate_phone_number(self, value):
        if not re.match(r'^\+998\d{9}$', value):
            raise serializers.ValidationError("Phone number must be +998XXXXXXXXX format.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class FactoryUserResetpasswordSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

# For backward compatibility if needed, but pointing to FactoryUser
class UnifiedUserSerializer(FactoryUserSerializer):
    pass

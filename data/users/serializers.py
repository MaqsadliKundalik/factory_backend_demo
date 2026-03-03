from rest_framework import serializers
from data.whouse.models import Whouse
from data.users.models import FactoryUser
import re

class FactoryUserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='role', read_only=True)
    
    class Meta:
        model = FactoryUser
        fields = [
            'id', 'name', 'phone_number', 'password', 'role', 'role_display',
            'crud_whouse_manager', 'crud_factory_operator', 'crud_driver', 
            'crud_guard', 'crud_product', 'crud_transport', 'crud_client', 
            'read_whouse', 'read_whouse_manager', 'read_factory_operator', 
            'read_driver', 'read_guard', 'read_product', 'read_transport', 
            'read_client', 'whouse'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
        read_only_fields = ['id']

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

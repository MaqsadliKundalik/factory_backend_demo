from rest_framework import serializers
from apps.drivers.models import Driver
from apps.guard.models import Guard
from apps.factory_operator.models import FactoryOperator
from apps.whouse_manager.models import WhouseManager
from data.whouse.models import Whouse
import re

class UnifiedUserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=25)
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.ChoiceField(choices=[
        ("manager", "Manager"),
        ("operator", "Operator"),
        ("driver", "Driver"),
        ("guard", "Guard")
    ], write_only=True)
    
    # Read-only fields for the response
    role_display = serializers.SerializerMethodField(read_only=True)
    whouses = serializers.SerializerMethodField(read_only=True)
    
    # Write-only fields for association
    whouse_id = serializers.UUIDField(write_only=True, required=False) # For FK models
    whouse_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False) # For M2M (Manager)
    
    # Driver specific fields
    car_type = serializers.CharField(max_length=10, required=False)
    car_number = serializers.CharField(max_length=15, required=False)

    created_at = serializers.DateTimeField(read_only=True)

    def get_role_display(self, obj):
        if isinstance(obj, WhouseManager):
            return "manager"
        elif isinstance(obj, FactoryOperator):
            return "operator"
        elif isinstance(obj, Driver):
            return "driver"
        elif isinstance(obj, Guard):
            return "guard"
        return "unknown"

    def get_whouses(self, obj):
        if isinstance(obj, WhouseManager):
            return [str(w.id) for w in obj.whouses.all()]
        elif hasattr(obj, 'whouse') and obj.whouse:
            return [str(obj.whouse.id)]
        return []

    def validate_phone_number(self, value):
        # Basic Uzbek phone number validation: +998901234567
        if not re.match(r'^\+998\d{9}$', value):
            raise serializers.ValidationError("Phone number must be +998XXXXXXXXX format.")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password', None)
        whouse_id = validated_data.pop('whouse_id', None)
        whouse_ids = validated_data.pop('whouse_ids', [])
        
        user_model = None
        if role == "manager":
            user_model = WhouseManager
        elif role == "operator":
            user_model = FactoryOperator
        elif role == "driver":
            user_model = Driver
        elif role == "guard":
            user_model = Guard
            
        instance = user_model(**validated_data)
        if password:
            instance.set_password(password)
        
        if role != "manager" and whouse_id:
            instance.whouse_id = whouse_id
        
        instance.save()
        
        if role == "manager" and whouse_ids:
            instance.whouses.set(whouse_ids)
            
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        whouse_id = validated_data.pop('whouse_id', None)
        whouse_ids = validated_data.pop('whouse_ids', None)
        
        # Role cannot be changed via update for simplicity/security in this unified view
        # If needed, it would involve deleting and re-creating
        validated_data.pop('role', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
            
        if not isinstance(instance, WhouseManager) and whouse_id:
            instance.whouse_id = whouse_id
            
        instance.save()
        
        if isinstance(instance, WhouseManager) and whouse_ids is not None:
            instance.whouses.set(whouse_ids)
            
        return instance
from rest_framework import serializers
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
        ("guard", "Guard")
    ], write_only=True)
    
    created_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        
        # Safely determine role
        role = "unknown"
        if isinstance(instance, WhouseManager): role = "manager"
        elif isinstance(instance, FactoryOperator): role = "operator"
        elif isinstance(instance, Guard): role = "guard"
        
        repr['role_display'] = role
        
        # Handle whouses based on role
        if role == "manager":
            repr['whouses'] = [str(w.id) for w in instance.whouses.all()]
        elif hasattr(instance, 'whouse') and instance.whouse:
            repr['whouses'] = [str(instance.whouse.id)]
        else:
            repr['whouses'] = []
            
        return repr

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
        elif role == "guard":
            user_model = Guard
            
        # Filter validated_data to only include fields present on the model
        model_fields = [f.name for f in user_model._meta.fields]
        create_data = {k: v for k, v in validated_data.items() if k in model_fields}
        
        instance = user_model(**create_data)
        if password:
            instance.set_password(password)
        
        if role != "manager" and whouse_id and 'whouse' in model_fields:
            instance.whouse_id = whouse_id
            
        instance.save()
        
        if role == "manager" and whouse_ids:
            instance.whouses.set(whouse_ids)
            
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        whouse_id = validated_data.pop('whouse_id', None)
        whouse_ids = validated_data.pop('whouse_ids', None)
        
        # Role cannot be changed via update
        validated_data.pop('role', None)

        model_fields = [f.name for f in instance.__class__._meta.fields]
        for attr, value in validated_data.items():
            if attr in model_fields:
                setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
            
        if not isinstance(instance, WhouseManager) and whouse_id and 'whouse' in model_fields:
            instance.whouse_id = whouse_id
            
        instance.save()
        
        if isinstance(instance, WhouseManager) and whouse_ids is not None:
            instance.whouses.set(whouse_ids)
            
        return instance
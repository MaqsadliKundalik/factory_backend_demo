from rest_framework import serializers
from .models import ProductType, ProductUnit, Product

class ProductTypeSerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ProductType
        fields = ['id', 'name', 'whouse', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductUnitSerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ProductUnit
        fields = ['id', 'name', 'whouse', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    types = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=ProductType.objects.all(),
        required=False
    )
    unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=ProductUnit.objects.all(),
        required=False
    )
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'types', 'unit', 'whouse', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['types'] = [{'id': t.id, 'name': t.name} for t in instance.types.all()]
        if instance.unit:
            repr['unit'] = {'id': instance.unit.id, 'name': instance.unit.name}
        return repr

    def create(self, validated_data):
        types_data = self.initial_data.get('types', [])
        unit_data = self.initial_data.get('unit')
        user = self.context['request'].user
        
        # Determine warehouse
        whouse = validated_data.get('whouse')
        if not whouse:
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse

        # Handle Unit
        unit_obj = None
        if unit_data:
            if isinstance(unit_data, int) or (isinstance(unit_data, str) and '-' in unit_data):
                unit_obj = ProductUnit.objects.filter(id=unit_data).first()
            
            if not unit_obj and isinstance(unit_data, str):
                unit_obj, _ = ProductUnit.objects.get_or_create(name=unit_data, whouse=whouse)
        
        # Handle Types
        type_objs = []
        for t_data in types_data:
            t_obj = None
            if isinstance(t_data, int) or (isinstance(t_data, str) and '-' in t_data):
                t_obj = ProductType.objects.filter(id=t_data).first()
            
            if not t_obj and isinstance(t_data, str):
                t_obj, _ = ProductType.objects.get_or_create(name=t_data, whouse=whouse)
            
            if t_obj:
                type_objs.append(t_obj)

        validated_data['unit'] = unit_obj
        validated_data['whouse'] = whouse
        
        validated_data.pop('types', []) 
        product = Product.objects.create(**validated_data)
        product.types.set(type_objs)
        return product

    def update(self, instance, validated_data):
        types_data = self.initial_data.get('types')
        unit_data = self.initial_data.get('unit')
        user = self.context['request'].user
        whouse = instance.whouse

        if unit_data is not None:
            unit_obj = None
            if isinstance(unit_data, int) or (isinstance(unit_data, str) and '-' in unit_data):
                unit_obj = ProductUnit.objects.filter(id=unit_data).first()
            
            if not unit_obj and isinstance(unit_data, str):
                unit_obj, _ = ProductUnit.objects.get_or_create(name=unit_data, whouse=whouse)
            validated_data['unit'] = unit_obj

        if types_data is not None:
            type_objs = []
            for t_data in types_data:
                t_obj = None
                if isinstance(t_data, int) or (isinstance(t_data, str) and '-' in t_data):
                    t_obj = ProductType.objects.filter(id=t_data).first()
                
                if not t_obj and isinstance(t_data, str):
                    t_obj, _ = ProductType.objects.get_or_create(name=t_data, whouse=whouse)
                
                if t_obj:
                    type_objs.append(t_obj)
            
            instance.types.set(type_objs)
            validated_data.pop('types', None)

        return super().update(instance, validated_data)

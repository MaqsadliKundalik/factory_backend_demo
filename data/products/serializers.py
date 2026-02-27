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

    def to_internal_value(self, data):
        # Support both ID and Name for on-the-fly creation
        # This is a bit tricky with SlugRelatedField if it doesn't exist
        # We'll handle custom logic in create/update or here
        return super().to_internal_value(data)

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
            if isinstance(unit_data, int):
                unit_obj = ProductUnit.objects.get(id=unit_data)
            else:
                unit_obj, _ = ProductUnit.objects.get_or_create(name=unit_data, whouse=whouse)
        
        # Handle Types
        type_objs = []
        for t_data in types_data:
            if isinstance(t_data, int):
                type_objs.append(ProductType.objects.get(id=t_data))
            else:
                t_obj, _ = ProductType.objects.get_or_create(name=t_data, whouse=whouse)
                type_objs.append(t_obj)

        validated_data['unit'] = unit_obj
        validated_data['whouse'] = whouse
        
        # types is M2M, needs to be set after create
        types = validated_data.pop('types', []) # Though SlugRelatedField might have handled some if they existed
        product = Product.objects.create(**validated_data)
        product.types.set(type_objs)
        return product
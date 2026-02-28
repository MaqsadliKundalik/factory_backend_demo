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
    types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ProductType.objects.all(),
        required=False
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=ProductUnit.objects.all(),
        required=False,
        allow_null=True
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
        user = self.context['request'].user
        
        whouse = validated_data.get('whouse')
        if not whouse:
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse

        validated_data['whouse'] = whouse
        
        types = validated_data.pop('types', [])
        product = Product.objects.create(**validated_data)
        product.types.set(types)
        return product

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

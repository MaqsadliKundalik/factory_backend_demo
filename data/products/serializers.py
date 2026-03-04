from rest_framework import serializers
from data.filedatas.models import File
from data.filedatas.serializers import FileSerializer
from data.whouse.serializers import WhouseSerializer
from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory, ProductItem

class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = ['id', 'name', 'type', 'unit', 'quantity', 'product']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.type:
            repr['type'] = ProductTypeSerializer(instance.type).data
        if instance.unit:
            repr['unit'] = ProductUnitSerializer(instance.unit).data
        if instance.product:
            repr['product'] = ProductSerializer(instance.product).data
        return repr

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'name', 'whouse']
        read_only_fields = ['id']

class ProductUnitSerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ProductUnit
        fields = ['id', 'name', 'whouse']
        read_only_fields = ['id']

class WhouseProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhouseProducts  
        fields = ['id', 'whouse', 'product', 'product_type', 'quantity', 'files', 'status']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.product:
            repr['product'] = ProductSerializer(instance.product).data
        if instance.product_type:
            repr['product_type'] = ProductTypeSerializer(instance.product_type).data
        repr['files'] = FileSerializer(instance.files, many=True).data
        repr['whouse'] = WhouseSerializer(instance.whouse).data
        return repr

    def validate(self, attrs):
        status = attrs.get('status')
        files = attrs.get('files', [])

        if status == 'created':
            if len(files) < 2:
                raise serializers.ValidationError({
                    "files": "Необходимо загрузить не менее 2 файлов."
                })
        return attrs

class SelectProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'types', 'unit', 'whouse', 'items']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['types'] = ProductTypeSerializer(instance.types, many=True).data
        if instance.unit:
            repr['unit'] = ProductUnitSerializer(instance.unit).data
        if instance.items:
            repr['items'] = ProductItemSerializer(instance.items, many=True).data
        return repr

    def create(self, validated_data):
        user = self.context['request'].user
        types = validated_data.pop('types', [])
        
        # Determine warehouse
        whouse = validated_data.get('whouse')
        if not whouse:
            whouse = user.whouses.first()
        validated_data['whouse'] = whouse

        product = Product.objects.create(**validated_data)
        product.types.set(types)

        return product

    def update(self, instance, validated_data):
        types = validated_data.pop('types', None)

        # Update basic fields
        instance = super().update(instance, validated_data)

        if types is not None:
            instance.types.set(types)

        return instance


class WhouseProductsHistorySerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    files = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    whouse_product = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = WhouseProductsHistory  
        fields = ['id', 'whouse_product', 'whouse', 'product', 'quantity', 'files', 'status']
        read_only_fields = ['id']



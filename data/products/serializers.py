from rest_framework import serializers
from data.filedatas.models import File
from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory, ProductItem

class ProductItemSerializer(serializers.ModelSerializer):
    type = serializers.PrimaryKeyRelatedField(queryset=ProductType.objects.all())
    unit = serializers.PrimaryKeyRelatedField(queryset=ProductUnit.objects.all())
    class Meta:
        model = ProductItem
        fields = ['id', 'type', 'unit', 'quantity']
        read_only_fields = ['id']

class ProductTypeSerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
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
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    files = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, required=False)
    product_type = serializers.PrimaryKeyRelatedField(queryset=ProductType.objects.all())
    class Meta:
        model = WhouseProducts  
        fields = ['id', 'whouse', 'product', 'product_type', 'quantity', 'files', 'status']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        # Add product details
        if instance.product:
            repr['product_details'] = {
                'id': instance.product.id,
                'name': instance.product.name
            }
        if instance.product_type:
            repr['product_type_details'] = {
                'id': instance.product_type.id,
                'name': instance.product_type.name
            }
        if instance.items:
            repr['items_details'] = [
                {'id': i.id, 'name': i.name, 'quantity': i.quantity, 'unit': i.unit, 'type': i.type} 
                for i in instance.items.all()
            ]
        repr['file_details'] = [
            {'id': f.id, 'url': f.file.url if f.file else None} 
            for f in instance.files.all()
        ]
        return repr

    def validate(self, attrs):
        status = attrs.get('status')
        files = attrs.get('files', [])

        if status == 'created':
            if len(files) < 2:
                raise serializers.ValidationError({
                    "files": "Kamida 2 ta fayl yuklanishi shart."
                })
        return attrs

class SelectProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']

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
    items = ProductItemSerializer(many=True, required=False, allow_null=True, allow_empty=True)
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'types', 'unit', 'whouse', 'items']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['types'] = [{'id': t.id, 'name': t.name} for t in instance.types.all()]
        if instance.unit:
            repr['unit'] = {'id': instance.unit.id, 'name': instance.unit.name}
        # Nested items representation is handled by the 'items' field defined above
        return repr

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('items', [])
        types = validated_data.pop('types', [])
        
        # Determine warehouse
        whouse = validated_data.get('whouse')
        if not whouse:
            whouse = user.whouses.first()
        validated_data['whouse'] = whouse

        product = Product.objects.create(**validated_data)
        product.types.set(types)

        # Create nested items
        for item_data in items_data:
            ProductItem.objects.create(product=product, **item_data)
        
        return product

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        types = validated_data.pop('types', None)

        # Update basic fields
        instance = super().update(instance, validated_data)

        if types is not None:
            instance.types.set(types)

        if items_data is not None:
            # Simple atomic replacement for items: 
            # delete old ones and create new ones to handle removals easily
            instance.items.all().delete()
            for item_data in items_data:
                ProductItem.objects.create(product=instance, **item_data)

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



from rest_framework import serializers
from data.filedatas.models import File
from app.settings import BASE_URL
from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory, ProductItem

class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = ['id', "product", 'type', 'unit', 'quantity']
        read_only_fields = ['id']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.type:
            repr['type'] = ProductTypeSerializer(instance.type).data
        if instance.unit:
            repr['unit'] = ProductUnitSerializer(instance.unit).data
        if instance.product:
            repr['product'] = {"id": instance.product.id, "name": instance.product.name} if instance.product else None
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
        fields = ['id', 'whouse', 'product', 'product_type', 'quantity', 'files', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.product:
            repr['product'] = ProductSerializer(instance.product).data
        if instance.product_type:
            repr['product_type'] = ProductTypeSerializer(instance.product_type).data
        repr['files'] = [{
            "id": file.id,
            "file": BASE_URL + file.file.url
        } for file in instance.files.all()]
        repr['whouse'] = {
            'id': instance.whouse.id,
            'name': instance.whouse.name
        }
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
    items = ProductItemSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'types', 'unit', 'whouse', 'items', 'created_at']
        read_only_fields = ['id', 'created_at']

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
    class Meta:
        model = WhouseProductsHistory  
        fields = ['id', 'whouse', 'product', 'quantity', 'status', "created_at"]
        read_only_fields = ['id', "created_at"]


class ProductAndItemCreateSerializer(serializers.ModelSerializer):
    items = ProductItemSerializer(many=True, required=True)
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
        items = validated_data.pop('items', [])
        
        # Determine warehouse
        whouse = validated_data.get('whouse')
        if not whouse:
            whouse = user.whouses.first()
        validated_data['whouse'] = whouse
        
        for item in items:
            product = item.get('product')
            # Product obyektini tekshirish
            if isinstance(product, str):
                # Agar string bo'lsa, UUID sifatida qidirish
                try:
                    product_obj = Product.objects.get(id=product)
                except Product.DoesNotExist:
                    raise serializers.ValidationError({"product": f"Product with id {product} not found"})
            elif hasattr(product, 'id'):
                # Agar Product obyekti bo'lsa
                product_obj = product
            else:
                raise serializers.ValidationError({"product": "Invalid product data"})
            
            # Product obyektini olib tashlab, qolgan maydonlarni saqlash
            item_data = {k: v for k, v in item.items() if k != 'product'}
            ProductItem.objects.create(product=product_obj, **item_data)

        return instance

    def update(self, instance, validated_data):
        user = self.context['request'].user
        types = validated_data.pop('types', None)
        items = validated_data.pop('items', None)
        
        # Determine warehouse
        whouse = validated_data.get('whouse')
        if whouse:
            validated_data['whouse'] = whouse
        elif not whouse and not instance.whouse:
            whouse = user.whouses.first()
            validated_data['whouse'] = whouse

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update types if provided
        if types is not None:
            instance.types.set(types)

        # Update items if provided
        if items is not None:
            # Remove existing items
            instance.items.all().delete()
            # Create new items
            for item in items:
                product_id = item.get('product')
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError({"product": "Product not found"})
                ProductItem.objects.create(product=product, **item)

        return instance

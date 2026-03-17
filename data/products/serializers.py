from rest_framework import serializers
from data.filedatas.models import File
from data.filedatas.serializers import FileSerializer
from app.settings import BASE_URL
from data.supplier.serializers import SupplierSerializer
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
        fields = ['id', 'whouse', 'product', "supplier", 'product_type', 'quantity', 'status', 'files', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.product:
            repr['product'] = ProductSerializer(instance.product).data

        if instance.product_type:
            repr['product_type'] = ProductTypeSerializer(instance.product_type).data

        if instance.supplier:
            repr['supplier'] = SupplierSerializer(instance.supplier).data

        
        repr['whouse'] = {
            'id': instance.whouse.id,
            'name': instance.whouse.name
        }
        repr['files'] = FileSerializer(instance.files.all(), many=True).data
        return repr

class WhouseProductActionSerializer(serializers.Serializer):
    supplier = serializers.UUIDField(required=False)

class WhouseProductsSerializerV2(serializers.ModelSerializer):
    files = serializers.ListField(child=serializers.FileField(), required=False, write_only=True)
    existing_files = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)

    class Meta:
        model = WhouseProducts
        fields = ['id', 'whouse', 'product', 'supplier', 'product_type', 'quantity', 'files', 'existing_files', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.product:
            repr['product'] = ProductSerializer(instance.product).data
        if instance.product_type:
            repr['product_type'] = ProductTypeSerializer(instance.product_type).data
        if instance.supplier:
            repr['supplier'] = SupplierSerializer(instance.supplier).data
        repr['whouse'] = {'id': instance.whouse.id, 'name': instance.whouse.name}
        repr['files'] = FileSerializer(instance.files.all(), many=True).data
        return repr

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if request is not None and self.instance is None:
            fields.pop('existing_files', None)
        return fields

    def _save_files(self, instance, files):
        for f in files:
            instance.files.add(f)

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        instance = super().create(validated_data)
        self._save_files(instance, files)
        return instance

    def update(self, instance, validated_data):
        files = validated_data.pop('files', None)
        existing_file_ids = validated_data.pop('existing_files', None)
        instance = super().update(instance, validated_data)
        if files is not None or existing_file_ids is not None:
            keep_ids = existing_file_ids or []
            files_to_delete = instance.files.exclude(id__in=keep_ids)
            File.objects.filter(id__in=files_to_delete.values_list('id', flat=True)).delete()
            if files:
                self._save_files(instance, files)
        return instance


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
        if instance.whouse:
            repr['whouse'] = {'id': instance.whouse.id, 'name': instance.whouse.name}
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
    supplier = serializers.PrimaryKeyRelatedField(read_only=True) 
    class Meta:
        model = WhouseProductsHistory  
        fields = ['id', 'whouse', 'product', 'supplier', 'quantity', 'status', "created_at"]
        read_only_fields = ['id', "created_at"]


class ProductItemWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = ProductItem
        fields = ['id', 'product', 'type', 'unit', 'quantity']
        read_only_fields = ['id']


class ProductAndItemCreateSerializer(serializers.ModelSerializer):
    items = ProductItemWriteSerializer(many=True, required=True)
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
        
        # Create product
        instance = Product.objects.create(**validated_data)
        
        # Add types
        instance.types.set(types)
        
        for item in items:
            product_obj = item.pop('product')
            ProductItem.objects.create(product=product_obj, **item)

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
                product_obj = item.pop('product')
                ProductItem.objects.create(product=product_obj, **item)

        return instance

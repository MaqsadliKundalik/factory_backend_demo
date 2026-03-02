from rest_framework import serializers
from data.filedatas.models import File
from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory

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
        fields = ['id', 'name', 'types', 'unit', 'whouse']
        read_only_fields = ['id']

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


class WhouseProductsHistorySerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    files = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    whouse_product = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = WhouseProductsHistory  
        fields = ['id', 'whouse_product', 'whouse', 'product', 'quantity', 'files', 'status']
        read_only_fields = ['id']
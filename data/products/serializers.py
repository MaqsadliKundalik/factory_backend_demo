from django.db import transaction
from rest_framework import serializers
from data.files.models import File
from data.files.serializers import FileSerializer
from app.settings import BASE_URL
from data.supplier.serializers import SupplierSerializer
from .models import (
    ProductType,
    ProductUnit,
    Product,
    WhouseProducts,
    WhouseProductsHistory,
    ProductItem,
)


class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItem
        fields = [
            "id",
            "raw_material",
            "product",
            "type",
            "unit",
            "quantity",
            "quantity_per_product",
        ]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.type:
            repr["type"] = ProductTypeSerializer(instance.type).data
        if instance.unit:
            repr["unit"] = ProductUnitSerializer(instance.unit).data
        if instance.product:
            repr["product"] = (
                {"id": instance.product.id, "name": instance.product.name}
                if instance.product
                else None
            )
        return repr


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "whouse"]
        read_only_fields = ["id"]


class ProductUnitSerializer(serializers.ModelSerializer):
    whouse = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductUnit
        fields = ["id", "name", "whouse"]
        read_only_fields = ["id"]


class WhouseProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhouseProducts
        fields = [
            "id",
            "whouse",
            "product",
            "supplier",
            "product_type",
            "quantity",
            "status",
            "files",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        if instance.product:
            repr["product"] = ProductSerializer(instance.product).data

        if instance.product_type:
            repr["product_type"] = ProductTypeSerializer(instance.product_type).data

        if instance.supplier:
            repr["supplier"] = SupplierSerializer(instance.supplier).data

        repr["whouse"] = {"id": instance.whouse.id, "name": instance.whouse.name}
        repr["files"] = FileSerializer(instance.files.all(), many=True).data
        return repr


class WhouseProductActionSerializer(serializers.Serializer):
    supplier = serializers.UUIDField(required=False)


class SelectProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    items = ProductItemSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "types", "unit", "whouse", "items", "created_at"]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["types"] = ProductTypeSerializer(instance.types, many=True).data
        if instance.unit:
            repr["unit"] = ProductUnitSerializer(instance.unit).data
        if instance.items:
            repr["items"] = ProductItemSerializer(instance.items, many=True).data
        if instance.whouse:
            repr["whouse"] = {"id": instance.whouse.id, "name": instance.whouse.name}
        return repr

    def create(self, validated_data):
        user = self.context["request"].user
        types = validated_data.pop("types", [])

        # Determine warehouse
        whouse = validated_data.get("whouse")
        if not whouse:
            whouse = user.whouses.first()
        validated_data["whouse"] = whouse

        product = Product.objects.create(**validated_data)
        product.types.set(types)

        return product

    def update(self, instance, validated_data):
        types = validated_data.pop("types", None)

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
        fields = [
            "id",
            "whouse",
            "product",
            "supplier",
            "quantity",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductItemWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = ProductItem
        fields = [
            "id",
            "raw_material",
            "product",
            "type",
            "unit",
            "quantity",
            "quantity_per_product",
        ]
        read_only_fields = ["id"]


class ProductAndItemCreateSerializer(serializers.ModelSerializer):
    items = ProductItemWriteSerializer(many=True, required=True)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Product
        fields = ["id", "name", "types", "unit", "whouse", "items", "quantity"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["types"] = ProductTypeSerializer(instance.types, many=True).data
        if instance.unit:
            repr["unit"] = ProductUnitSerializer(instance.unit).data
        if instance.items:
            repr["items"] = ProductItemSerializer(instance.items, many=True).data
        return repr

    def create(self, validated_data):
        user = self.context["request"].user
        types = validated_data.pop("types", [])
        items = validated_data.pop("items", [])
        quantity = validated_data.pop("quantity", 0)

        # Determine warehouse
        whouse = validated_data.get("whouse")
        if not whouse:
            whouse = user.whouses.first()
        validated_data["whouse"] = whouse

        # Create product
        instance = Product.objects.create(**validated_data)

        # Add types
        instance.types.set(types)

        for item in items:
            item.pop("product", None)
            ProductItem.objects.create(product=instance, **item)

        return instance

    def update(self, instance, validated_data):
        user = self.context["request"].user
        types = validated_data.pop("types", None)
        items = validated_data.pop("items", None)
        quantity = validated_data.pop("quantity", None)

        # Determine warehouse
        whouse = validated_data.get("whouse")
        if whouse:
            validated_data["whouse"] = whouse
        elif not whouse and not instance.whouse:
            whouse = user.whouses.first()
            validated_data["whouse"] = whouse

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update types if provided
        if types is not None:
            instance.types.set(types)

        # Update items if provided
        if items is not None:
            with transaction.atomic():
                instance.items.all().delete()
                for item in items:
                    item.pop("product", None)
                    ProductItem.objects.create(product=instance, **item)

        return instance


class SelectWhouseProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = WhouseProducts
        fields = ["id", "product_name"]
        read_only_fields = ["id"]
    
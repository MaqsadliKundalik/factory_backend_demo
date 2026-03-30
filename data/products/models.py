from django.db import models
from apps.common.models import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.supplier.models import Supplier
    from data.users.models import FactoryUser
    from data.whouse.models import Whouse
    from data.orders.models import SubOrderItem


class HistoryStatus(models.TextChoices):
    IN = "IN", "In"
    OUT = "OUT", "Out"


class ProductType(BaseModel):
    name = models.CharField(max_length=255)
    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name


class ProductUnit(BaseModel):
    name = models.CharField(max_length=255)
    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=255)
    types = models.ManyToManyField("products.ProductType", related_name="products")
    unit: ProductUnit = models.ForeignKey(
        "products.ProductUnit",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )

    items = "QuerySet[ProductItem]"

    def __str__(self):
        return self.name


class WhouseProducts(BaseModel):
    """
    PENDING - qorovul qoshsa tushadigan status
    CREATED - skladchi qo’shsa tushadigan status
    REJECTED - skladchi qorovul qo’shgan mahsulotni rad etsa chiqadigan status
    CONFIRMED - skladchi qorovul qo'shgan mahsulotni tasdiqlaydi
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CREATED = "CREATED", "Created"
        REJECTED = "REJECTED", "Rejected"
        CONFIRMED = "CONFIRMED", "Confirmed"

    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )
    product: Product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    supplier: "Supplier | None" = models.ForeignKey(
        "supplier.Supplier", on_delete=models.CASCADE, null=True, blank=True
    )
    product_type: ProductType = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    files = models.ManyToManyField(
        "files.File", blank=True, related_name="whouse_product_files"
    )
    creator: "FactoryUser | None" = models.ForeignKey(
        "users.FactoryUser", on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return self.product.name


class ProductItem(BaseModel):
    product: Product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="items"
    )
    raw_material: "Product | None" = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="used_in",
        null=True,
        blank=True,
    )
    type: "ProductType | None" = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )
    unit: "ProductUnit | None" = models.ForeignKey(
        ProductUnit,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_per_product = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class WhouseProductsHistory(BaseModel):
    order_item: "SubOrderItem | None" = models.ForeignKey(
        "orders.SubOrderItem", on_delete=models.CASCADE, null=True, blank=True
    )
    product: "Product | None" = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="history",
        null=True,
        blank=True,
    )
    product_type: "ProductType | None" = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, null=True, blank=True
    )
    whouse: "Whouse | None" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier: "Supplier | None" = models.ForeignKey(
        "supplier.Supplier", on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=HistoryStatus.choices, default=HistoryStatus.IN
    )

    def __str__(self):
        return f"History of {self.product.name} at {self.created_at}"

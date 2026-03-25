from typing import TYPE_CHECKING

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from apps.common.models import BaseModel


if TYPE_CHECKING:
    from data.products.models import ProductType, ProductUnit, Product
    from data.files.models import File
    from data.clients.models import Client, ClientBranches
    from data.drivers.models import Driver
    from data.transports.models import Transport
    from data.whouse.models import Whouse
    from data.users.models import FactoryUser


# Create your models here.
class Order(BaseModel):
    """
        NEW - Buyurtma yaratilgach shu statusda bo’ladi

    IN_PROGRESS - JArayon boshlandi. Ya’ni buyurtmadagi mahsulot tayyorlana boshladi.

    ON_WAY - haydovchi yo’lga chiqqach buyurtmani shu statusga o’tkazadi

    ARRIVED - Haydovchi manzilga yetib kelgach buyurtmani shu holatga o’tkazadi

    UNLOADING - Haydovchi yukni tushirishni boshlaganida shu statusga o’tkazadi

    COMPLETED - Yukni tushirib bo’lgach shu statusga o’tkazadi. Lekin bu holatga o’tkazishidan oldin fayl so’rashi kerak. ya’ni rasm kamida 2ta rasm. va mijozni imzosini talab qilishi kerak
    """

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ON_WAY = "ON_WAY", "On Way"
        ARRIVED = "ARRIVED", "Arrived"
        UNLOADING = "UNLOADING", "Unloading"
        COMPLETED = "COMPLETED", "Completed"
        REJECTED = "REJECTED", "Rejected"

    class Rejector(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        OPERATOR = "OPERATOR", "Operator"
        MANAGER = "MANAGER", "Manager"

    display_id = models.PositiveIntegerField(unique=True, editable=False, null=True)
    client: "Client" = models.ForeignKey(
        "clients.Client", on_delete=models.PROTECT, related_name="orders"
    )
    branch: "ClientBranches" = models.ForeignKey(
        "clients.ClientBranches", on_delete=models.PROTECT, related_name="orders"
    )
    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse", on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    rejector_role = models.CharField(
        max_length=20, choices=Rejector.choices, null=True, blank=True
    )
    rejector_id = models.UUIDField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.display_id:
            last_order = Order.all_objects.all().order_by("display_id").last()
            self.display_id = (
                (last_order.display_id + 1)
                if last_order and last_order.display_id
                else 1
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ord-{self.display_id:03}" if self.display_id else f"Ord-{self.id}"


class SubOrder(BaseModel):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ON_WAY = "ON_WAY", "On Way"
        ARRIVED = "ARRIVED", "Arrived"
        UNLOADING = "UNLOADING", "Unloading"
        COMPLETED = "COMPLETED", "Completed"
        REJECTED = "REJECTED", "Rejected"

    order: "Order" = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="sub_orders"
    )
    driver: "Driver" = models.ForeignKey(
        "factory_drivers.Driver", on_delete=models.PROTECT, related_name="sub_orders"
    )
    transport: "Transport" = models.ForeignKey(
        "transports.Transport", on_delete=models.PROTECT, related_name="sub_orders"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    status_history = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    sign: "File" = models.ForeignKey(
        "files.File",
        on_delete=models.PROTECT,
        related_name="sub_orders_sign",
        null=True,
        blank=True,
    )
    files = models.ManyToManyField(
        "files.File", blank=True, related_name="sub_orders_files", null=True
    )

    def __str__(self):
        display_name = (
            f"Ord-{self.order.display_id:03}"
            if self.order.display_id
            else f"Ord-{self.order.id}"
        )
        return f"SubOrd-{self.id} for {display_name}"


class OrderItem(BaseModel):
    order: "Order" = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="order_items"
    )
    product: "Product" = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="order_items"
    )
    type: "ProductType" = models.ForeignKey(
        "products.ProductType", on_delete=models.PROTECT, related_name="order_items"
    )
    unit: "ProductUnit" = models.ForeignKey(
        "products.ProductUnit", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"OrderItem-{self.id} for {self.order}"


class SubOrderItem(BaseModel):
    sub_order: "SubOrder" = models.ForeignKey(
        "orders.SubOrder", on_delete=models.CASCADE, related_name="sub_order_items"
    )
    product: "Product" = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="sub_order_items"
    )
    type: "ProductType" = models.ForeignKey(
        "products.ProductType", on_delete=models.PROTECT, related_name="sub_order_items"
    )
    unit: "ProductUnit" = models.ForeignKey(
        "products.ProductUnit", on_delete=models.PROTECT, related_name="sub_order_items"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"SubOrderItem-{self.id} for {self.sub_order}"

from django.db import models, transaction
from django.db.models import Max
from django.core.serializers.json import DjangoJSONEncoder
from apps.common.models import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.whouse.models import Whouse
    from data.drivers.models import Driver
    from data.transports.models import Transport
    from data.files.models import File


class ExcavatorOrder(BaseModel):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        PAUSED = "PAUSED", "Paused"
        COMPLETED = "COMPLETED", "Completed"
        EXPIRED = "EXPIRED", "Expired"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    display_id = models.PositiveIntegerField(unique=True, editable=False, null=True)

    client_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    lat = models.FloatField()
    lon = models.FloatField()
    address = models.CharField(max_length=512, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    files = models.ManyToManyField(
        "files.File", blank=True, related_name="excavator_order_files"
    )

    whouse: "Whouse" = models.ForeignKey(
        "factory_whouse.Whouse",
        on_delete=models.PROTECT,
        related_name="excavator_orders",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.display_id:
            last_order = ExcavatorOrder.all_objects.all().order_by("display_id").last()
            self.display_id = (
                (last_order.display_id + 1)
                if last_order and last_order.display_id
                else 1
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"ExcOrd-{self.display_id:03}" if self.display_id else f"ExcOrd-{self.id}"
        )


class ExcavatorSubOrder(BaseModel):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        PAUSED = "PAUSED", "Paused"
        COMPLETED = "COMPLETED", "Completed"
        EXPIRED = "EXPIRED", "Expired"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"

    parent: "ExcavatorOrder" = models.ForeignKey(
        "excavator.ExcavatorOrder", on_delete=models.CASCADE, related_name="sub_orders"
    )
    driver: "Driver" = models.ForeignKey(
        "factory_drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="excavator_sub_orders",
    )

    transport: "Transport" = models.ForeignKey(
        "transports.Transport",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="excavator_sub_orders",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    status_history = models.JSONField(default=list, encoder=DjangoJSONEncoder)

    before_sign: "File" = models.ForeignKey(
        "files.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="excavator_sub_orders_before_sign",
    )
    before_files = models.ManyToManyField(
        "files.File", blank=True, related_name="excavator_suborder_before_files"
    )
    after_sign: "File" = models.ForeignKey(
        "files.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="excavator_sub_orders_after_sign",
    )
    after_files = models.ManyToManyField(
        "files.File", blank=True, related_name="excavator_suborder_after_files"
    )

    def __str__(self):
        return f"ExcSubOrd-{self.id} for {self.parent}"

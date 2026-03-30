from django.db import models
from apps.common.models import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.excavator.models import ExcavatorSubOrder
    from data.orders.models import SubOrder


class NotificationTargetObject(models.TextChoices):
    EXCAVATOR_SUB_ORDER = "EXCAVATOR_SUB_ORDER", "Excavator Sub Order"
    SUB_ORDER = "SUB_ORDER", "Sub Order"

# Create your models here.
class Notification(BaseModel):
    title = models.CharField(max_length=255)
    message = models.TextField()

    from_role = models.CharField(max_length=255)
    to_role = models.CharField(max_length=255)
    to_user_id = models.UUIDField(
        null=True, blank=True
    )  # agar berilsa, faqat shu usergagina

    is_read = models.BooleanField(default=False)

    readonly_fields = ["created_at", "updated_at"]

    date_hierarchy = "created_at"
    target_type = models.CharField(
        max_length=255,
        choices=NotificationTargetObject.choices,
        null=True,
        blank=True,
    )
    excavator_obj: "ExcavatorSubOrder" = models.ForeignKey(
        "excavator.ExcavatorSubOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    order_obj: "SubOrder" = models.ForeignKey(
        "orders.SubOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    def __str__(self):
        return self.title

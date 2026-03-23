from django.db import models
from apps.common.models import BaseModel


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

    def __str__(self):
        return self.title

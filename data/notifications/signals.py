from django.dispatch import receiver
from django.db.models.signals import post_save

from django.db import transaction
import logging

from data.notifications.models import Notification
from data.notifications.tasks import send_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def on_new_notification(sender, instance, created: bool, **kwargs):

    if not created:
        logger.info(
            "Notification post_save skipped because created=False for notification_id=%s",
            instance.id,
        )
        return

    logger.info(
        "Notification created notification_id=%s to_role=%s to_user_id=%s title=%s",
        instance.id,
        instance.to_role,
        instance.to_user_id,
        instance.title,
    )

    def enqueue():

        logger.info(
            "Enqueuing send_notification task for notification_id=%s after transaction commit",
            instance.id,
        )
        async_result = send_notification.delay(instance.id)
        logger.info(
            "send_notification task queued for notification_id=%s celery_task_id=%s",
            instance.id,
            async_result.id,
        )

    transaction.on_commit(enqueue)

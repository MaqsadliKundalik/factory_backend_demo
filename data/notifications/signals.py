from django.dispatch import receiver
from django.db.models.signals import post_save

from django.db import transaction

from data.notifications.models import Notification
from data.notifications.tasks import send_notification


@receiver(post_save, sender=Notification)
def on_new_notification(sender, instance, created: bool, **kwargs):

    if not created:
        return

    def enqueue():

        send_notification.delay(instance.id)

    transaction.on_commit(enqueue)

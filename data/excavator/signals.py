from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from .models import ExcavatorOrder, ExcavatorSubOrder
from data.products.models import WhouseProductsHistory
from data.drivers.models import Driver
from data.notifications.models import Notification, NotificationTargetObject

logger = logging.getLogger(__name__)



@receiver(post_save, sender=ExcavatorSubOrder)
def create_excavator_suborder_notification(sender, instance: ExcavatorSubOrder, created, **kwargs):
    if created and instance.status == ExcavatorSubOrder.Status.NEW and instance.driver and instance.driver.type == Driver.Type.INTERNAL:
        logger.info(
            "Creating NEW ExcavatorSubOrder notification for suborder_id=%s driver_id=%s parent_order_id=%s",
            instance.id,
            instance.driver.id,
            instance.parent_id,
        )
        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="Новый заказ",
            message=f"Вам назначен новый заказ №{instance.parent.display_id}.",
            target_type=NotificationTargetObject.EXCAVATOR_SUB_ORDER,
            excavator_obj=instance,
        )
    
    elif created and instance.status == ExcavatorSubOrder.Status.REJECTED and instance.driver and instance.driver.type == Driver.Type.INTERNAL:
        logger.info(
            "Creating REJECTED ExcavatorSubOrder notification for suborder_id=%s driver_id=%s parent_order_id=%s",
            instance.id,
            instance.driver.id,
            instance.parent_id,
        )
        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="Заказ отклонён",
            message=f"Заказ №{instance.parent.display_id} был отклонён.",
            target_type=NotificationTargetObject.EXCAVATOR_SUB_ORDER,
            excavator_obj=instance,
        )

    
@receiver(post_save, sender=ExcavatorOrder)
def create_excavator_order_notification(sender, instance, created, **kwargs):
    pass
    # if instance.status == ExcavatorOrder.Status.PAUSED:
    #     instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz vaqtinchalik to'xtatildi")
    # elif instance.status == ExcavatorOrder.Status.COMPLETED:
    #     instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz tugallandi")
    # elif instance.status == ExcavatorOrder.Status.EXPIRED:
    #     instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz muddati tugadi")
    # elif instance.status == ExcavatorOrder.Status.REJECTED:
    #     instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz rad etildi")
    


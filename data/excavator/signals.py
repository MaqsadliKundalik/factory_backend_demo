from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ExcavatorOrder, ExcavatorSubOrder
from data.products.models import WhouseProductsHistory
from data.drivers.models import Driver
from data.notifications.models import Notification



@receiver(post_save, sender=ExcavatorSubOrder)
def create_excavator_suborder_notification(sender, instance, created, **kwargs):
    if created and instance.status == ExcavatorSubOrder.Status.NEW and instance.driver and instance.driver.type == Driver.Type.INTERNAL:
        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="ExcavatorSubOrder is created",
            message=f"ExcavatorSubOrder {instance.display_id} is created",
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
    


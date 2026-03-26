from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ExcavatorOrder, ExcavatorSubOrder
from data.products.models import WhouseProductsHistory
from data.notifications.models import Notification



@receiver(post_save, sender=ExcavatorSubOrder)
def update_whouse_product_history(sender, instance, created, **kwargs):
    if created and instance.status == ExcavatorSubOrder.Status.NEW:
        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="ExcavatorSubOrder is created",
            message=f"ExcavatorSubOrder {instance.display_id} is created",
        )
    elif instance.status == ExcavatorSubOrder.Status.IN_PROGRESS:
        instance.order.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz jarayonida")
    elif instance.status == ExcavatorSubOrder.Status.PAUSED:
        instance.order.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz vaqtinchalik to'xtatildi")
    elif instance.status == ExcavatorSubOrder.Status.COMPLETED:
        instance.order.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz tugallandi")
    elif instance.status == ExcavatorSubOrder.Status.EXPIRED:
        instance.order.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz muddati tugadi")
    elif instance.status == ExcavatorSubOrder.Status.REJECTED:
        instance.order.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz rad etildi")
    


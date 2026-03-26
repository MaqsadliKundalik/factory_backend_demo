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
    
@receiver(post_save, sender=ExcavatorOrder)
def update_whouse_product_history(sender, instance, created, **kwargs):
    if instance.status == ExcavatorOrder.Status.IN_PROGRESS:
        instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz jarayonida")
    elif instance.status == ExcavatorOrder.Status.PAUSED:
        instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz vaqtinchalik to'xtatildi")
    elif instance.status == ExcavatorOrder.Status.COMPLETED:
        instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz tugallandi")
    elif instance.status == ExcavatorOrder.Status.EXPIRED:
        instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz muddati tugadi")
    elif instance.status == ExcavatorOrder.Status.REJECTED:
        instance.client.send_sms(f"Sizning {instance.display_id} raqamli buyurtmangiz rad etildi")
    


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubOrder
from data.products.models import WhouseProductsHistory
from data.notifications.models import Notification



@receiver(post_save, sender=SubOrder)
def update_whouse_product_history(sender, instance, **kwargs):
    if instance.status == SubOrder.Status.NEW:
        WhouseProductsHistory.objects.create(
            whouse=instance.order.whouse,
            product=instance.order.product,
            quantity=instance.quantity,
            status='OUT'  # HistoryStatus.OUT
        )
        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="SubOrder is created",
            message=f"SubOrder {instance.id} is created",
        )
    # elif instance.status == SubOrder.Status.IN_PROGRESS:
    #     instance.order.client.send_sms("SubOrder is in progress")
    # elif instance.status == SubOrder.Status.ON_WAY:
    #     instance.order.client.send_sms("SubOrder is on way")
    # elif instance.status == SubOrder.Status.ARRIVED:
    #     instance.order.client.send_sms("SubOrder is arrived")
    # elif instance.status == SubOrder.Status.UNLOADING:
    #     instance.order.client.send_sms("SubOrder is unloading")
    # elif instance.status == SubOrder.Status.COMPLETED:
    #     instance.order.client.send_sms("SubOrder is completed")
    


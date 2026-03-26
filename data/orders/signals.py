from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubOrder
from data.products.models import WhouseProductsHistory
from data.notifications.models import Notification


@receiver(post_save, sender=SubOrder)
def update_whouse_product_history(sender, instance, created, **kwargs):
    if created and instance.status == SubOrder.Status.NEW:
        for item in instance.sub_order_items.all():
            WhouseProductsHistory.objects.create(
                order_item=item,
                whouse=instance.order.whouse,
                product=item.product,
                quantity=item.quantity,
                status="OUT",
            )

        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="Order is created",
            message=f"Order {instance.id} is created",
        )
    else:
        for item in instance.sub_order_items.all():
            WhouseProductsHistory.objects.update_or_create(
                order_item=item,
                defaults={
                    "whouse": instance.order.whouse,
                    "product": item.product,
                    "quantity": item.quantity,
                    "status": "OUT",
                },
            )

    if instance.status == SubOrder.Status.ON_WAY:
        instance.order.client.send_sms(
            f"Sizning {instance.id} raqamli buyurtmangizdan quyidagilar yo'lga chiqdi.\n\n"
            + "\n".join([f"- {item.product.name} ({item.quantity})" for item in instance.sub_order_items.all()])
        )

 

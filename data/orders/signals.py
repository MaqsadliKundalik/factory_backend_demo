from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SubOrder
from data.drivers.models import Driver
from data.products.models import WhouseProductsHistory
from data.notifications.models import Notification, NotificationTargetObject


@receiver(post_save, sender=SubOrder)
def create_suborder_notification_and_history(sender, instance: SubOrder, created, **kwargs):
    if created and instance.status == SubOrder.Status.NEW and instance.driver and instance.driver.type == Driver.Type.INTERNAL:
        for item in instance.sub_order_items.all():
            WhouseProductsHistory.objects.create(
                order_item=item,
                whouse=instance.order.whouse,
                product=item.product,
                product_type=item.type,
                quantity=item.quantity,
                status="OUT",
            )

        Notification.objects.create(
            from_role="admin",
            to_role="driver",
            to_user_id=instance.driver.id,
            title="Новый заказ",
            message=f"Вам назначен новый заказ №{instance.order.display_id}.",
            target_type=NotificationTargetObject.SUB_ORDER,
            order_obj=instance,
        )
    else:
        if instance.status == SubOrder.Status.REJECTED and instance.driver and instance.driver.type == Driver.Type.INTERNAL:
            Notification.objects.create(
                from_role="admin",
                to_role="driver",
                to_user_id=instance.driver.id,
                title="Заказ отклонён",
                message=f"Заказ №{instance.order.display_id} был отклонён.",
                target_type=NotificationTargetObject.SUB_ORDER,
                order_obj=instance,
            )
        for item in instance.sub_order_items.all():
            WhouseProductsHistory.objects.update_or_create(
                order_item=item,
                defaults={
                    "whouse": instance.order.whouse,
                    "product": item.product,
                    "product_type": item.type,
                    "quantity": item.quantity,
                    "status": "OUT",
                },
            )

    # if instance.status == SubOrder.Status.ON_WAY:
    #     instance.order.client.send_sms(
    #         f"Sizning {instance.id} raqamli buyurtmangizdan quyidagilar yo'lga chiqdi.\n\n"
    #         + "\n".join([f"- {item.product.name} ({item.quantity})" for item in instance.sub_order_items.all()])
    #     )

 

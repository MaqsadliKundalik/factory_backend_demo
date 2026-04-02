from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from .models import SubOrder, Order
from data.drivers.models import Driver
from data.products.models import WhouseProductsHistory
from data.notifications.models import Notification, NotificationTargetObject
from data.reports.services import generate_yuk_xati_short_url
import time

logger = logging.getLogger(__name__)

def _format_order_items_for_sms(order: Order):
    items = order.order_items.select_related("product", "type", "unit")
    return "\n".join(
        [
            "- {name} {type_name} ({quantity} {unit})".format(
                name=item.product.name,
                type_name=item.type.name,
                quantity=item.quantity,
                unit=item.unit.name,
            ).strip()
            for item in items
        ]
    )


def _format_completed_order_items_for_sms(order: Order):
    completed_items = {}
    completed_sub_orders = order.sub_orders.filter(status=SubOrder.Status.COMPLETED).prefetch_related(
        "sub_order_items__product", "sub_order_items__type", "sub_order_items__unit"
    )
    for sub_order in completed_sub_orders:
        for item in sub_order.sub_order_items.all():
            key = (item.product.name, item.type.name, item.unit.name)
            completed_items[key] = completed_items.get(key, 0) + item.quantity
    return "\n".join(
        [
            "- {name} {type_name} ({quantity} {unit})".format(
                name=name,
                type_name=type_name,
                quantity=quantity,
                unit=unit,
            ).strip()
            for (name, type_name, unit), quantity in completed_items.items()
        ]
    )

@receiver(post_save, sender=Order)
def order_signals(sender, instance: Order, created, **kwargs):
    print(f"Sending sms {instance.status}")

    if created and instance.status == Order.Status.NEW:
        items_text = _format_order_items_for_sms(instance)
        sms_message = "Уважаемый клиент, ваш заказ №{id} был успешно оформлен.".format(
            id=instance.display_id
        )
        if items_text:
            sms_message += "\n\nСостав заказа:\n{items}".format(items=items_text)
        instance.client.send_sms(
            sms_message
        )
    
    if instance.status == Order.Status.REJECTED:
        instance.client.send_sms(
            "Уважаемый клиент, ваш заказ №{instance.display_id} был отменён.".format(instance=instance)
        )

    if instance.status == Order.Status.COMPLETED:
        print("Tayyorlanmoqda")
        sms_message = "Уважаемый клиент, ваш заказ №{instance.display_id} был успешно завершён.".format(instance=instance)
        completed_items_text = _format_completed_order_items_for_sms(instance)
        if completed_items_text:
            sms_message += "\n\nДоставленные товары:\n{items}".format(items=completed_items_text)
        yuk_xati_url = generate_yuk_xati_short_url(instance.id)
        if yuk_xati_url:
            sms_message += "\n\nТоварно-транспортная накладная: {yuk_xati_url}".format(yuk_xati_url=yuk_xati_url)
        print("Tayor\n\n{msg}".format(msg=sms_message))       
        instance.client.send_sms(sms_message)


@receiver(post_save, sender=SubOrder)
def create_suborder_notification_and_history(sender, instance: SubOrder, created, **kwargs):
    if created and instance.status == SubOrder.Status.NEW and instance.driver and instance.driver.type == Driver.Type.INTERNAL:
        logger.info(
            "Creating NEW SubOrder notification for suborder_id=%s driver_id=%s order_id=%s",
            instance.id,
            instance.driver.id,
            instance.order_id,
        )
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
            logger.info(
                "Creating REJECTED SubOrder notification for suborder_id=%s driver_id=%s order_id=%s created=%s",
                instance.id,
                instance.driver.id,
                instance.order_id,
                created,
            )
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
    print(f"Sending sms {instance.status}")

    if instance.status == SubOrder.Status.ON_WAY:
        instance.order.client.send_sms(
            "Уважаемый клиент, по вашему заказу №{instance.order.display_id} следующие товары были отправлены на доставку.\n\n".format(instance=instance)
            + "\n".join(["- {item.product.name} ({item.quantity})".format(item=item) for item in instance.sub_order_items.all()])
        )
    elif instance.status == SubOrder.Status.ARRIVED:
        instance.order.client.send_sms(
            "Уважаемый клиент, по вашему заказу №{instance.order.display_id} следующие товары были доставлены по адресу назначения.\n\n".format(instance=instance)
            + "\n".join(["- {item.product.name} ({item.quantity})".format(item=item) for item in instance.sub_order_items.all()])
        )
    elif instance.status == SubOrder.Status.UNLOADING:
        instance.order.client.send_sms(
            "Уважаемый клиент, по вашему заказу №{instance.order.display_id} началась разгрузка следующих товаров.\n\n".format(instance=instance)
            + "\n".join(["- {item.product.name} ({item.quantity})".format(item=item) for item in instance.sub_order_items.all()])
        )

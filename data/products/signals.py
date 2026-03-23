from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WhouseProducts, WhouseProductsHistory, HistoryStatus, ProductItem
from data.notifications.models import Notification


@receiver(post_save, sender=WhouseProducts)
def create_whouse_product_history(sender, instance, **kwargs):
    if instance.status == WhouseProducts.Status.PENDING:
        Notification.objects.create(
            to_role="whouse_manager",
            from_role="guard",
            title="New product added",
            message=f"New product {instance.product.name} added to whouse {instance.whouse.name}",
        )

    WhouseProductsHistory.objects.create(
        wproduct=instance,
        whouse=instance.whouse,
        product=instance.product,
        quantity=instance.quantity,
        supplier=instance.supplier,
        status=HistoryStatus.IN,
    )


@receiver(post_save, sender=WhouseProducts)
def update_whouse_product_history_extra(sender, instance, **kwargs):
    if instance.status == WhouseProducts.Status.CREATED:
        WhouseProductsHistory.objects.create(
            wproduct=instance,
            whouse=instance.whouse,
            product=instance.product,
            quantity=instance.quantity,
            supplier=instance.supplier,
            status=HistoryStatus.IN,
        )


@receiver(post_save, sender=WhouseProductsHistory)
def update_whouse_product_history(sender, instance, **kwargs):
    if instance.status == HistoryStatus.OUT:
        wproduct = instance.wproduct
        wproduct.quantity -= instance.quantity
        wproduct.save()
    else:
        wproduct = instance.wproduct
        wproduct.quantity += instance.quantity
        wproduct.save()


@receiver(post_save, sender=ProductItem)
def create_product_item_history(sender, instance, created, **kwargs):
    if not created:
        return

    WhouseProductsHistory.objects.create(
        wproduct=instance.raw_material,
        whouse=instance.raw_material.whouse,
        product=instance.product,
        quantity=instance.quantity,
        status=HistoryStatus.OUT,
    )

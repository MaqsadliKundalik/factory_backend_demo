from itertools import product
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WhouseProducts, WhouseProductsHistory, HistoryStatus, ProductItem
from data.notifications.models import Notification


@receiver(post_save, sender=WhouseProducts)
def create_whouse_product_history(sender, instance, created, **kwargs):
    # Faqat yangi yaratilganda ishlaydi
    if not created:
        return
    
    if instance.status == WhouseProducts.Status.PENDING:
        Notification.objects.create(
            to_role="whouse_manager",
            from_role="guard",
            title="New product added",
            message=f"New product {instance.product.name} added to whouse {instance.whouse.name}",
        )

    # Asosiy mahsulot tarixini yaratish
    WhouseProductsHistory.objects.create(
        wproduct=instance,
        whouse=instance.whouse,
        product=instance.product,
        quantity=instance.quantity,
        supplier=instance.supplier,
        status=HistoryStatus.IN,
    )
    
    # Agar mahsulotning xomashyolari bo'lsa, ularni ayirish
    if instance.product.items.exists():
        for item in instance.product.items.all():
            if not item.raw_material:
                continue
            
            # Kerakli xomashyo miqdorini hisoblash
            # Formula: (instance.quantity / item.quantity_per_product) * item.quantity
            if item.quantity_per_product == 0:
                continue
                
            needed_raw_material = (instance.quantity / item.quantity_per_product) * item.quantity
            
            # Xomashyo yetarli ekanligini tekshirish
            if item.raw_material.quantity < needed_raw_material:
                # Xomashyo yetarli emas - notification yuborish
                Notification.objects.create(
                    to_role="whouse_manager",
                    from_role="system",
                    title="Insufficient raw materials",
                    message=f"Not enough {item.raw_material.product.name} for {instance.product.name}. Need {needed_raw_material}, have {item.raw_material.quantity}",
                )
                continue
            
            # Xomashyoni ayirish
            item.raw_material.quantity -= needed_raw_material
            item.raw_material.save()
            
            # Tarixga yozish (OUT)
            WhouseProductsHistory.objects.create(
                wproduct=item.raw_material,
                whouse=instance.whouse,
                product=item.raw_material.product,
                quantity=needed_raw_material,
                status=HistoryStatus.OUT,
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

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WhouseProducts, WhouseProductsHistory, HistoryStatus, ProductItem, Product
from data.notifications.models import Notification


@receiver(post_save, sender=WhouseProducts)
def create_whouse_product_history(sender, instance, created, **kwargs):
    # Faqat yangi yaratilganda ishlaydi
    if not created:
        return
    


    # Asosiy mahsulot tarixini yaratish
    WhouseProductsHistory.objects.create(
        whouse=instance.whouse,
        product=instance.product,
        product_type=instance.product_type,
        quantity=instance.quantity,
        supplier=instance.supplier,
        status=HistoryStatus.IN,
    )
    
    # Agar mahsulotning xomashyolari bo'lsa, ularni ayirish
    if instance.product.items.exists():
        for item in instance.product.items.all():
            if not item.raw_material:
                continue
            
            if item.quantity_per_product == 0:
                continue
                
            needed_raw_material = (instance.quantity / item.quantity_per_product) * item.quantity
            
            WhouseProductsHistory.objects.create(
                product=item.raw_material,
                whouse=instance.whouse,
                product_type=item.type,
                quantity=needed_raw_material,
                status=HistoryStatus.OUT,
            )


@receiver(post_save, sender=WhouseProducts)
def update_whouse_product_history_extra(sender, instance, **kwargs):
    if instance.status == WhouseProducts.Status.CREATED:
        WhouseProductsHistory.objects.create(
            whouse=instance.whouse,
            product=instance.product,
            product_type=instance.product_type,
            quantity=instance.quantity,
            supplier=instance.supplier,
            status=HistoryStatus.IN,
        )


# @receiver(post_save, sender=WhouseProductsHistory)
# def update_whouse_product_history(sender, instance, **kwargs):
#     if instance.status == HistoryStatus.OUT:
#         wproduct = instance.wproduct
#         wproduct.quantity -= instance.quantity
#         wproduct.save()
#     else:
#         wproduct = instance.wproduct
#         wproduct.quantity += instance.quantity
#         wproduct.save()


@receiver(post_save, sender=ProductItem)
def create_product_item_history(sender, instance, created, **kwargs):
    if not created:
        return

    WhouseProductsHistory.objects.create(
        whouse=instance.raw_material.whouse,
        product=instance.raw_material,
        product_type=instance.type,
        quantity=instance.quantity,
        status=HistoryStatus.OUT,
    )

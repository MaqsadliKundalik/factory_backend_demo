from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WhouseProducts, WhouseProductsHistory, HistoryStatus, ProductItem, Product
from data.notifications.models import Notification


@receiver(post_save, sender=WhouseProducts)
def create_whouse_product_history(sender, instance, created, **kwargs):
    # Faqat yangi yaratilganda ishlaydi
    if not created and instance.product.items.exists():
        return
    


    # Asosiy mahsulot tarixini yaratish
    WhouseProductsHistory.objects.create(
        whouse=instance.whouse,
        product=instance.product,
        product_type=instance.product_type,
        quantity=instance.quantity,
        supplier=instance.supplier,
        status=HistoryStatus.IN,
        obj_status=instance.status,
    )
    

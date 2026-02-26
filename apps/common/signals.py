from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.whouse_manager.models import WhouseManager
from apps.factory_operator.models import FactoryOperator
from .models import UserPermissions

@receiver(post_save, sender=WhouseManager)
def create_manager_permissions(sender, instance, created, **kwargs):
    if created:
        UserPermissions.objects.create(
            content_object=instance,
            crud_whouse=True,
            read_whouse=True,
            crud_whouse_manager=True,
            read_whouse_manager=True,
            crud_factory_operator=True,
            read_factory_operator=True,
            crud_driver=True,
            read_driver=True,
            crud_guard=True,
            read_guard=True,
            crud_product_type=True,
            read_product_type=True
        )

@receiver(post_save, sender=FactoryOperator)
def create_operator_permissions(sender, instance, created, **kwargs):
    if created:
        UserPermissions.objects.create(
            content_object=instance,
            crud_whouse=True,
            read_whouse=True,
            crud_whouse_manager=False,
            read_whouse_manager=True,
            crud_factory_operator=False,
            read_factory_operator=True,
            crud_driver=True,
            read_driver=True,
            crud_guard=True,
            read_guard=True,
            crud_product_type=True,
            read_product_type=True
        )

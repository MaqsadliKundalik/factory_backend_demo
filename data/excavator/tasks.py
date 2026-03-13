from celery import shared_task
from datetime import date


@shared_task
def expire_excavator_orders():
    from .models import ExcavatorOrder, ExcavatorSubOrder

    today = date.today()

    expired_orders = ExcavatorOrder.objects.filter(
        end_date__lt=today,
    ).exclude(
        status__in=[ExcavatorOrder.Status.COMPLETED, ExcavatorOrder.Status.EXPIRED]
    )
    count_orders = expired_orders.update(status=ExcavatorOrder.Status.EXPIRED)

    expired_sub_orders = ExcavatorSubOrder.objects.filter(
        end_date__lt=today,
    ).exclude(
        status__in=[ExcavatorSubOrder.Status.COMPLETED, ExcavatorSubOrder.Status.EXPIRED]
    )
    count_sub_orders = expired_sub_orders.update(status=ExcavatorSubOrder.Status.EXPIRED)

    return f"Expired: {count_orders} orders, {count_sub_orders} sub_orders"

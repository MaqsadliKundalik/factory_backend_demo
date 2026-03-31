import io
import logging
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from openpyxl import Workbook

from data.orders.models import Order
from data.reports.views import fill_yuk_xati

logger = logging.getLogger(__name__)


YUK_XATI_PREFETCH = (
    'order_items__product', 'order_items__type', 'order_items__unit',
    'sub_orders__driver', 'sub_orders__transport',
    'sub_orders__sub_order_items__product',
    'sub_orders__sub_order_items__type',
    'sub_orders__sub_order_items__unit',
)


def get_yuk_xati_order(order_id):
    return (
        Order.objects
        .select_related('client', 'branch')
        .prefetch_related(*YUK_XATI_PREFETCH)
        .filter(id=order_id)
        .first()
    )


def build_yuk_xati_workbook(order):
    wb = Workbook()
    fill_yuk_xati(wb.active, order)
    return wb


def save_yuk_xati_file(order):
    workbook = build_yuk_xati_workbook(order)
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    file_name = f"files/yuk_xati_{order.id}.xlsx"
    if default_storage.exists(file_name):
        default_storage.delete(file_name)
    saved_name = default_storage.save(file_name, ContentFile(buffer.getvalue()))
    relative_url = default_storage.url(saved_name)
    return urljoin(f"{settings.BASE_URL.rstrip('/')}/", relative_url.lstrip('/'))


def shorten_url(url):
    response = requests.get(
        'https://is.gd/create.php',
        params={'format': 'simple', 'url': url},
        timeout=10,
    )
    if response.status_code == 200:
        short_url = response.text.strip()
        if short_url.startswith('https://is.gd/'):
            return short_url

    return url


def generate_yuk_xati_short_url(order_id):
    order = get_yuk_xati_order(order_id)
    if not order:
        return None

    file_url = save_yuk_xati_file(order)
    return shorten_url(file_url)

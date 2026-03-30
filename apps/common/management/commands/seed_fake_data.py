"""
Fake data seeder for statistics and testing.
Usage:
    python manage.py seed_fake_data
    python manage.py seed_fake_data --orders 1000 --excavators 200 --months 12
"""
import random
import string
from datetime import timedelta, date, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

# ── Uzbek fake name pools ────────────────────────────────────────────────────

FIRST_NAMES = [
    "Alisher", "Bobur", "Dilshod", "Eldor", "Farrux",
    "Husan", "Islom", "Jahongir", "Kamol", "Lochin",
    "Mansur", "Nodir", "Otabek", "Pahlavon", "Ravshan",
    "Sanjar", "Temur", "Ulugbek", "Vohid", "Zafar",
    "Aziz", "Behruz", "Davron", "Ergash", "Firdavs",
    "Hamid", "Ibrohim", "Jamshid", "Komil", "Laziz",
]
LAST_NAMES = [
    "Karimov", "Rahimov", "Toshmatov", "Yusupov", "Xolmatov",
    "Nazarov", "Mirzayev", "Ismoilov", "Abdullayev", "Holiqov",
    "Qodirov", "Sultonov", "Baxtiyorov", "Ergashev", "Normatov",
    "Xasanov", "Umarov", "Turgunov", "Sotvoldiyev", "Razzaqov",
]
COMPANY_SUFFIXES = ["Qurilish", "Savdo", "Logistika", "Holding", "Group", "Taminot", "Zavod", "Fabrika"]
COMPANY_PREFIXES = ["Mega", "Super", "Ulug'", "Baraka", "Nur", "Zafar", "Omad", "Fayz", "Sarvar", "Gold"]

ADDRESSES = [
    "Toshkent, Chilonzor tumani, 5-mavze",
    "Toshkent, Yunusobod tumani, Amir Temur ko'chasi",
    "Samarqand, Registon ko'chasi 12",
    "Buxoro, Navoiy ko'chasi 45",
    "Namangan, Yangi hayot ko'chasi 8",
    "Andijon, Asaka yo'li 33",
    "Farg'ona, Mustaqillik ko'chasi 21",
    "Qo'qon, Shahrisabz ko'chasi 7",
    "Nukus, Xiva ko'chasi 18",
    "Urganch, Beruniy ko'chasi 4",
    "Jizzax, Sharq ko'chasi 15",
    "Termiz, Amudaryo ko'chasi 9",
    "Qarshi, Nishon yo'li 22",
    "Guliston, Baynal-Milal ko'chasi 3",
    "Navoiy, Metallurglar ko'chasi 11",
]

PRODUCT_TYPES = [
    "M200 Beton", "M250 Beton", "M300 Beton", "M350 Beton", "M400 Beton",
    "Qorishmali", "Oddiy", "Maxsus", "Armaturali", "Engil",
]
PRODUCT_UNITS = ["m³", "tonna", "dona", "kg", "litr"]
PRODUCTS = [
    "Beton", "Qum", "Shag'al", "Sement", "Temir armatura",
    "G'isht", "Blok", "Plita", "Qorishmali beton", "Asfalt",
]

# Coordinates (Uzbekistan approximate)
UZ_LAT_RANGE = (37.2, 41.9)
UZ_LON_RANGE = (56.0, 73.1)

PHONE_PREFIXES = ["90", "91", "93", "94", "95", "97", "98", "99", "33", "88", "77"]


def _rand_phone():
    return f"+998{random.choice(PHONE_PREFIXES)}{random.randint(1000000, 9999999)}"


def _rand_inn():
    return str(random.randint(100000000, 999999999))


def _rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _rand_company():
    return f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"


def _rand_date_in_range(start_dt, end_dt):
    delta = end_dt - start_dt
    return start_dt + timedelta(days=random.randint(0, delta.days))


def _rand_coords():
    lat = round(random.uniform(*UZ_LAT_RANGE), 6)
    lon = round(random.uniform(*UZ_LON_RANGE), 6)
    return lat, lon


def _build_status_history(statuses_chain, start_dt):
    """
    statuses_chain — list of statuses in order, e.g. ['NEW', 'ON_WAY', 'COMPLETED']
    Returns a JSONField-compatible list with timestamp entries.
    Each status lasts between 5 and 240 minutes.
    """
    history = []
    current = start_dt
    for status in statuses_chain:
        history.append({
            'status': status,
            'timestamp': current.isoformat(),
        })
        current = current + timedelta(minutes=random.randint(5, 240))
    return history


ORDER_STATUS_CHAINS = {
    'NEW':       ['NEW'],
    'ON_WAY':    ['NEW', 'ON_WAY'],
    'ARRIVED':   ['NEW', 'ON_WAY', 'ARRIVED'],
    'UNLOADING': ['NEW', 'ON_WAY', 'ARRIVED', 'UNLOADING'],
    'COMPLETED': ['NEW', 'ON_WAY', 'ARRIVED', 'UNLOADING', 'COMPLETED'],
    'REJECTED':  ['NEW', 'REJECTED'],
}

EXC_STATUS_CHAINS = {
    'NEW':         ['NEW'],
    'PAUSED':      ['NEW', 'PAUSED'],
    'COMPLETED':   ['NEW', 'COMPLETED'],
    'EXPIRED':     ['NEW', 'EXPIRED'],
}


class Command(BaseCommand):
    help = "Seed the database with fake data for statistics"

    def add_arguments(self, parser):
        parser.add_argument("--orders", type=int, default=500, help="Number of orders to create (default: 500)")
        parser.add_argument("--excavators", type=int, default=100, help="Number of excavator orders (default: 100)")
        parser.add_argument("--months", type=int, default=12, help="Spread data over last N months (default: 12)")
        parser.add_argument("--clients", type=int, default=30, help="Ensure at least N clients exist (default: 30)")
        parser.add_argument("--suppliers", type=int, default=15, help="Ensure at least N suppliers exist (default: 15)")
        parser.add_argument("--drivers", type=int, default=20, help="Ensure at least N drivers exist (default: 20)")
        parser.add_argument("--transports", type=int, default=15, help="Ensure at least N transports exist (default: 15)")

    def handle(self, *args, **options):
        from data.whouse.models import Whouse
        from data.products.models import Product, ProductType, ProductUnit, WhouseProducts, WhouseProductsHistory, HistoryStatus
        from data.clients.models import Client, ClientBranches
        from data.supplier.models import Supplier
        from data.drivers.models import Driver
        from data.transports.models import Transport
        from data.orders.models import Order, SubOrder, OrderItem, SubOrderItem
        from data.excavator.models import ExcavatorOrder, ExcavatorSubOrder

        whouses = list(Whouse.objects.all())
        if not whouses:
            raise CommandError("Hech qanday Whouse topilmadi! Avval kamida bitta warehouse yarating.")

        self.stdout.write(f"Topildi: {len(whouses)} ta warehouse")

        end_dt = timezone.now()
        start_dt = end_dt - timedelta(days=options["months"] * 30)

        # ── 1. Ensure base data ──────────────────────────────────────────────
        self.stdout.write("Base ma'lumotlar tekshirilmoqda...")

        product_types = self._ensure_product_types(ProductType, whouses)
        product_units = self._ensure_product_units(ProductUnit, whouses)
        products = self._ensure_products(Product, product_types, product_units, whouses)
        clients = self._ensure_clients(Client, ClientBranches, whouses, options["clients"])
        suppliers = self._ensure_suppliers(Supplier, whouses, options["suppliers"])
        drivers = self._ensure_drivers(Driver, whouses, options["drivers"])
        transports = self._ensure_transports(Transport, whouses, options["transports"])

        self.stdout.write(f"  ProductTypes: {len(product_types)}, Units: {len(product_units)}, Products: {len(products)}")
        self.stdout.write(f"  Clients: {len(clients)}, Suppliers: {len(suppliers)}")
        self.stdout.write(f"  Drivers: {len(drivers)}, Transports: {len(transports)}")

        # ── 2. WhouseProducts (inventory entries) ────────────────────────────
        self.stdout.write("WhouseProducts yaratilmoqda...")
        whouse_products = self._create_whouse_products(
            WhouseProducts, WhouseProductsHistory, HistoryStatus, products, product_types, suppliers, whouses, start_dt, end_dt
        )
        self.stdout.write(f"  {len(whouse_products)} ta WhouseProducts yaratildi")

        # ── 3. Orders ────────────────────────────────────────────────────────
        self.stdout.write(f"{options['orders']} ta Order yaratilmoqda...")
        orders_created = self._create_orders(
            Order, SubOrder, OrderItem, SubOrderItem, WhouseProductsHistory, HistoryStatus,
            clients, products, product_types, product_units, whouses, drivers, transports,
            options["orders"], start_dt, end_dt
        )
        self.stdout.write(f"  {orders_created} ta Order va SubOrder yaratildi")

        # ── 4. Excavator orders ──────────────────────────────────────────────
        self.stdout.write(f"{options['excavators']} ta ExcavatorOrder yaratilmoqda...")
        exc_created = self._create_excavator_orders(
            ExcavatorOrder, ExcavatorSubOrder,
            whouses, drivers, transports,
            options["excavators"], start_dt, end_dt
        )
        self.stdout.write(f"  {exc_created} ta ExcavatorOrder yaratildi")

        self.stdout.write(self.style.SUCCESS("\nSeeding muvaffaqiyatli yakunlandi!"))
        self.stdout.write(self.style.SUCCESS(
            f"Yaratildi: {orders_created} orders, {exc_created} excavator orders"
        ))

    # ── Helper: ensure base entities ─────────────────────────────────────────

    def _ensure_product_types(self, ProductType, whouses):
        existing = list(ProductType.objects.all())
        needed = max(0, 5 - len(existing))
        new_types = []
        for i in range(needed):
            whouse = random.choice(whouses)
            pt = ProductType.objects.create(name=PRODUCT_TYPES[i % len(PRODUCT_TYPES)], whouse=whouse)
            new_types.append(pt)
        return existing + new_types

    def _ensure_product_units(self, ProductUnit, whouses):
        existing = list(ProductUnit.objects.all())
        needed = max(0, 4 - len(existing))
        new_units = []
        for i in range(needed):
            whouse = random.choice(whouses)
            pu = ProductUnit.objects.create(name=PRODUCT_UNITS[i % len(PRODUCT_UNITS)], whouse=whouse)
            new_units.append(pu)
        return existing + new_units

    def _ensure_products(self, Product, product_types, product_units, whouses):
        existing = list(Product.objects.all())
        needed = max(0, 6 - len(existing))
        new_products = []
        for i in range(needed):
            whouse = random.choice(whouses)
            unit = random.choice(product_units) if product_units else None
            prod = Product.objects.create(
                name=PRODUCTS[i % len(PRODUCTS)],
                unit=unit,
                whouse=whouse,
            )
            # Assign random types
            types_to_add = random.sample(product_types, min(2, len(product_types)))
            prod.types.set(types_to_add)
            new_products.append(prod)
        return existing + new_products

    def _ensure_clients(self, Client, ClientBranches, whouses, min_count):
        existing = list(Client.objects.all())
        needed = max(0, min_count - len(existing))
        new_clients = []
        for _ in range(needed):
            whouse = random.choice(whouses)
            client = Client.objects.create(
                name=_rand_company(),
                inn_number=_rand_inn(),
                whouse=whouse,
            )
            # Create 1-3 branches per client
            for j in range(random.randint(1, 3)):
                lat, lon = _rand_coords()
                ClientBranches.objects.create(
                    client=client,
                    name=f"Filial {j + 1}",
                    address=random.choice(ADDRESSES),
                    longitude=lon,
                    latitude=lat,
                )
            new_clients.append(client)
        # Ensure every client has at least one branch
        for client in existing:
            if not client.branches.exists():
                lat, lon = _rand_coords()
                ClientBranches.objects.create(
                    client=client,
                    name="Asosiy filial",
                    address=random.choice(ADDRESSES),
                    longitude=lon,
                    latitude=lat,
                )
        return existing + new_clients

    def _ensure_suppliers(self, Supplier, whouses, min_count):
        existing = list(Supplier.objects.all())
        needed = max(0, min_count - len(existing))
        new_suppliers = []
        for _ in range(needed):
            whouse = random.choice(whouses)
            sup_type = random.choice([Supplier.Type.INTERNAL, Supplier.Type.EXTERNAL])
            kwargs = dict(name=_rand_company(), type=sup_type, whouse=whouse)
            if sup_type == Supplier.Type.INTERNAL:
                kwargs["inn_number"] = _rand_inn()
            supplier = Supplier.objects.create(**kwargs)
            new_suppliers.append(supplier)
        return existing + new_suppliers

    def _ensure_drivers(self, Driver, whouses, min_count):
        existing = list(Driver.objects.all())
        needed = max(0, min_count - len(existing))
        new_drivers = []
        used_phones = set(Driver.all_objects.values_list("phone_number", flat=True))
        for _ in range(needed):
            whouse = random.choice(whouses)
            # generate unique phone
            for _ in range(20):
                phone = _rand_phone()
                if phone not in used_phones:
                    break
            else:
                continue
            used_phones.add(phone)
            driver = Driver(
                name=_rand_name(),
                phone_number=phone,
                type=Driver.Type.INTERNAL,
                whouse=whouse,
            )
            driver.set_password("12345678")
            driver.save()
            new_drivers.append(driver)
        return existing + new_drivers

    def _ensure_transports(self, Transport, whouses, min_count):
        existing = list(Transport.objects.all())
        needed = max(0, min_count - len(existing))
        new_transports = []
        for _ in range(needed):
            whouse = random.choice(whouses)
            letters = "".join(random.choices(string.ascii_uppercase, k=2))
            digits = "".join(random.choices(string.digits, k=4))
            number = f"{letters}{digits}UZ"
            transport = Transport.objects.create(
                name=f"Yuk mashinasi {number}",
                number=number,
                type=Transport.Type.INTERNAL,
                car_type=Transport.CarType.TRUCK,
                whouse=whouse,
            )
            new_transports.append(transport)
        return existing + new_transports

    # ── Helper: create whouse products ───────────────────────────────────────

    def _create_whouse_products(self, WhouseProducts, WhouseProductsHistory, HistoryStatus, products, product_types, suppliers, whouses, start_dt, end_dt):
        created = []
        for whouse in whouses:
            whouse_suppliers = [s for s in suppliers if s.whouse_id == whouse.pk] or suppliers
            for product in random.sample(products, min(len(products), 5)):
                ptype = random.choice(product_types)
                supplier = random.choice(whouse_suppliers)
                qty = Decimal(str(round(random.uniform(100, 5000), 2)))
                wp = WhouseProducts.objects.create(
                    whouse=whouse,
                    product=product,
                    supplier=supplier,
                    product_type=ptype,
                    quantity=qty,
                    status=WhouseProducts.Status.CONFIRMED,
                )
                # History IN record
                hist = WhouseProductsHistory.objects.create(
                    product=product,
                    product_type=ptype,
                    whouse=whouse,
                    quantity=qty,
                    supplier=supplier,
                    status=HistoryStatus.IN,
                )
                fake_dt = _rand_date_in_range(start_dt.date(), end_dt.date())
                fake_aware = timezone.make_aware(
                    timezone.datetime(fake_dt.year, fake_dt.month, fake_dt.day, random.randint(6, 20), random.randint(0, 59))
                )
                WhouseProducts.objects.filter(pk=wp.pk).update(created_at=fake_aware)
                WhouseProductsHistory.objects.filter(pk=hist.pk).update(created_at=fake_aware)
                created.append(wp)
        return created

    # ── Helper: create orders ─────────────────────────────────────────────────

    def _create_orders(self, Order, SubOrder, OrderItem, SubOrderItem,
                       WhouseProductsHistory, HistoryStatus,
                       clients, products, product_types, product_units,
                       whouses, drivers, transports,
                       count, start_dt, end_dt):
        statuses = [
            Order.Status.NEW, Order.Status.ON_WAY,
            Order.Status.ARRIVED, Order.Status.UNLOADING, Order.Status.COMPLETED,
            Order.Status.COMPLETED, Order.Status.COMPLETED,  # weight COMPLETED more
            Order.Status.REJECTED,
        ]
        sub_statuses = [
            SubOrder.Status.NEW, SubOrder.Status.ON_WAY,
            SubOrder.Status.ARRIVED, SubOrder.Status.UNLOADING, SubOrder.Status.COMPLETED,
            SubOrder.Status.COMPLETED, SubOrder.Status.COMPLETED,
        ]

        orders_created = 0
        sub_orders_batch = []
        hist_batch = []

        for _ in range(count):
            whouse = random.choice(whouses)
            whouse_clients = [c for c in clients if c.whouse_id == whouse.pk]
            client = random.choice(whouse_clients) if whouse_clients else random.choice(clients)
            branches = list(client.branches.all())
            if not branches:
                continue
            branch = random.choice(branches)
            order_status = random.choice(statuses)

            fake_dt = _rand_date_in_range(start_dt.date(), end_dt.date())
            fake_aware = timezone.make_aware(
                timezone.datetime(fake_dt.year, fake_dt.month, fake_dt.day,
                                  random.randint(6, 20), random.randint(0, 59))
            )

            rejector_role = None
            if order_status == Order.Status.REJECTED:
                rejector_role = random.choice(list(Order.Rejector.values))

            order = Order.objects.create(
                client=client,
                branch=branch,
                whouse=whouse,
                status=order_status,
                rejector_role=rejector_role,
            )
            Order.objects.filter(pk=order.pk).update(created_at=fake_aware)
            orders_created += 1

            # Create 1-3 OrderItems
            item_count = random.randint(1, 3)
            order_items = []
            for _ in range(item_count):
                product = random.choice(products)
                ptype = random.choice(product_types)
                punit = random.choice(product_units)
                qty = Decimal(str(round(random.uniform(5, 500), 2)))
                price = Decimal(str(round(random.uniform(50000, 500000), 2)))
                order_items.append(OrderItem(
                    order=order,
                    product=product,
                    type=ptype,
                    unit=punit,
                    quantity=qty,
                    price=price,
                ))
            OrderItem.objects.bulk_create(order_items)

            # Create 1-3 SubOrders
            sub_count = random.randint(1, 3)
            total_qty = sum(item.quantity for item in order_items)
            remaining_qty = total_qty
            for s in range(sub_count):
                driver = random.choice(drivers)
                transport = random.choice(transports)
                sub_qty = remaining_qty if s == sub_count - 1 else Decimal(str(round(float(remaining_qty) * random.uniform(0.3, 0.7), 2)))
                remaining_qty -= sub_qty
                sub_status = random.choice(sub_statuses)
                chain = ORDER_STATUS_CHAINS.get(sub_status, ['NEW'])
                status_history = _build_status_history(chain, fake_aware)

                sub = SubOrder(
                    order=order,
                    driver=driver,
                    transport=transport,
                    quantity=sub_qty,
                    status=sub_status,
                    status_history=status_history,
                )
                sub_orders_batch.append((sub, fake_aware, order, order_items, sub_qty))

        # Bulk create SubOrders
        sub_objs = [item[0] for item in sub_orders_batch]
        created_subs = SubOrder.objects.bulk_create(sub_objs)

        sub_order_items_batch = []
        for i, sub in enumerate(created_subs):
            _, fake_aware, order, order_items, sub_qty = sub_orders_batch[i]
            SubOrder.objects.filter(pk=sub.pk).update(created_at=fake_aware)

            # Create SubOrderItems mirroring OrderItems with proportional quantities
            total_order_qty = sum(item.quantity for item in order_items)
            ratio = (sub_qty / total_order_qty) if total_order_qty else Decimal("1")
            for oi in order_items:
                sub_item_qty = Decimal(str(round(float(oi.quantity * ratio), 2)))
                sub_order_items_batch.append(SubOrderItem(
                    sub_order=sub,
                    product=oi.product,
                    type=oi.type,
                    unit=oi.unit,
                    quantity=sub_item_qty,
                ))

            hist_batch.append(WhouseProductsHistory(
                whouse=order.whouse,
                product=order_items[0].product if order_items else None,
                product_type=order_items[0].type if order_items else None,
                quantity=sub_qty,
                status=HistoryStatus.OUT,
            ))

        if sub_order_items_batch:
            SubOrderItem.objects.bulk_create(sub_order_items_batch)

        if hist_batch:
            WhouseProductsHistory.objects.bulk_create(hist_batch)

        return orders_created

    # ── Helper: create excavator orders ──────────────────────────────────────

    def _create_excavator_orders(self, ExcavatorOrder, ExcavatorSubOrder,
                                 whouses, drivers, transports, count, start_dt, end_dt):
        statuses = [
            ExcavatorOrder.Status.NEW,
            ExcavatorOrder.Status.PAUSED, ExcavatorOrder.Status.COMPLETED,
            ExcavatorOrder.Status.COMPLETED,  # weight COMPLETED
            ExcavatorOrder.Status.EXPIRED,
        ]
        payment_statuses = [
            ExcavatorOrder.PaymentStatus.PENDING,
            ExcavatorOrder.PaymentStatus.PAID,
            ExcavatorOrder.PaymentStatus.PAID,
        ]
        sub_statuses = [
            ExcavatorSubOrder.Status.NEW,
            ExcavatorSubOrder.Status.PAUSED, ExcavatorSubOrder.Status.COMPLETED,
            ExcavatorSubOrder.Status.COMPLETED,
        ]

        created = 0
        sub_batch = []

        for _ in range(count):
            whouse = random.choice(whouses)
            lat, lon = _rand_coords()
            fake_dt = _rand_date_in_range(start_dt.date(), end_dt.date())
            fake_aware = timezone.make_aware(
                timezone.datetime(fake_dt.year, fake_dt.month, fake_dt.day,
                                  random.randint(6, 20), random.randint(0, 59))
            )
            duration_days = random.randint(1, 14)
            exc_order = ExcavatorOrder.objects.create(
                client_name=_rand_name(),
                phone_number=_rand_phone(),
                lat=lat,
                lon=lon,
                address=random.choice(ADDRESSES),
                start_date=fake_dt,
                end_date=fake_dt + timedelta(days=duration_days),
                comment=None,
                status=random.choice(statuses),
                payment_status=random.choice(payment_statuses),
                whouse=whouse,
            )
            ExcavatorOrder.objects.filter(pk=exc_order.pk).update(created_at=fake_aware)
            created += 1

            # 1-2 sub orders
            for _ in range(random.randint(1, 2)):
                driver = random.choice(drivers) if drivers else None
                transport = random.choice(transports) if transports else None
                exc_sub_status = random.choice(sub_statuses)
                chain = EXC_STATUS_CHAINS.get(exc_sub_status, ['NEW'])
                status_history = _build_status_history(chain, fake_aware)
                sub = ExcavatorSubOrder(
                    parent=exc_order,
                    driver=driver,
                    transport=transport,
                    status=exc_sub_status,
                    status_history=status_history,
                )
                sub_batch.append((sub, fake_aware))

        # Bulk create ExcavatorSubOrders
        subs = ExcavatorSubOrder.objects.bulk_create([s for s, _ in sub_batch])
        for i, sub in enumerate(subs):
            _, fake_aware = sub_batch[i]
            ExcavatorSubOrder.objects.filter(pk=sub.pk).update(created_at=fake_aware)

        return created

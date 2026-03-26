from datetime import date, timedelta
from unittest.mock import patch, MagicMock, PropertyMock
from uuid import uuid4

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from data.excavator.models import ExcavatorOrder, ExcavatorSubOrder
from data.drivers.models import Driver
from data.transports.models import Transport
from data.whouse.models import Whouse
from data.files.models import File


# Disable signals globally for all tests
PATCH_SIGNALS = patch("data.excavator.signals.post_save")
PATCH_MIXIN = patch(
    "apps.common.mixins.PermissionMetaMixin.get_permissions_meta",
    return_value={"can_access": True, "can_edit": True, "can_read": True},
)


def create_mock_user():
    """Create a mock user with required attributes."""
    user = MagicMock()
    user.id = uuid4()
    user.is_authenticated = True
    user.EXCAVATORS_PAGE = True
    user.name = "Test User"
    user.has_perm = MagicMock(return_value=True)
    user.whouses = MagicMock()
    user.whouses.exists.return_value = False
    user.__class__.__name__ = "FactoryUser"
    return user


class AuthMixin:
    """Mixin to handle authentication and request attributes in API tests."""

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = create_mock_user()

        # Patch authentication
        self.auth_patcher = patch(
            "apps.common.auth.authentication.UnifiedJWTAuthentication.authenticate",
            return_value=(self.user, None),
        )
        # Patch permissions
        self.perm_patcher = patch(
            "apps.common.permissions.HasDynamicPermission.has_permission",
            return_value=True,
        )
        # Patch permission meta mixin
        self.mixin_patcher = patch(
            "apps.common.mixins.PermissionMetaMixin.get_permissions_meta",
            return_value={"can_access": True, "can_edit": True, "can_read": True},
        )
        # Patch signals to avoid instance.client.send_sms errors
        self.signal_patcher = patch(
            "data.excavator.signals.receiver", lambda *a, **kw: lambda f: f
        )

        self.auth_patcher.start()
        self.perm_patcher.start()
        self.mixin_patcher.start()

        # Patch request attributes via middleware
        from django.test import RequestFactory

        original_request = APIClient.request

        user = self.user

        def patched_request(client_self, **kwargs):
            response = original_request(client_self, **kwargs)
            return response

        # Use handler to set request attributes
        self.handler_patcher = patch(
            "rest_framework.views.APIView.initialize_request",
            wraps=self._wrap_initialize_request,
        )

    def _wrap_initialize_request(self, original_request, *args, **kwargs):
        from rest_framework.views import APIView

        # Call original
        request = APIView.initialize_request(
            self._current_view, original_request, *args, **kwargs
        )
        request.driver = None
        request.guard = None
        request.operator = self.user
        request.manager = None
        return request

    def tearDown(self):
        self.auth_patcher.stop()
        self.perm_patcher.stop()
        self.mixin_patcher.stop()
        super().tearDown()


# ===================== MODEL TESTS =====================


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ExcavatorOrderModelTest(TestCase):

    def setUp(self):
        # Disconnect signals to avoid errors
        from django.db.models.signals import post_save
        from data.excavator import signals

        post_save.disconnect(dispatch_uid=None, sender=ExcavatorOrder)
        post_save.disconnect(dispatch_uid=None, sender=ExcavatorSubOrder)
        self.whouse = Whouse.objects.create(name="Test Warehouse")

    def test_create_order_with_auto_display_id(self):
        """Test that display_id auto-increments."""
        order1 = ExcavatorOrder.objects.create(
            client_name="Client A",
            phone_number="+998901111111",
            lat=41.311,
            lon=69.279,
            start_date=date.today(),
        )
        self.assertEqual(order1.display_id, 1)

        order2 = ExcavatorOrder.objects.create(
            client_name="Client B",
            phone_number="+998902222222",
            lat=41.312,
            lon=69.280,
            start_date=date.today() + timedelta(days=1),
        )
        self.assertEqual(order2.display_id, 2)

    def test_order_default_status(self):
        order = ExcavatorOrder.objects.create(
            client_name="Client",
            phone_number="+998903333333",
            lat=41.0,
            lon=69.0,
        )
        self.assertEqual(order.status, ExcavatorOrder.Status.NEW)
        self.assertEqual(order.payment_status, ExcavatorOrder.PaymentStatus.PENDING)

    def test_order_str(self):
        order = ExcavatorOrder.objects.create(
            client_name="Client",
            phone_number="+998904444444",
            lat=41.0,
            lon=69.0,
        )
        self.assertIn("ExcOrd-", str(order))

    def test_soft_delete(self):
        order = ExcavatorOrder.objects.create(
            client_name="Client",
            phone_number="+998905555555",
            lat=41.0,
            lon=69.0,
        )
        order.delete()
        self.assertEqual(ExcavatorOrder.objects.count(), 0)
        self.assertEqual(ExcavatorOrder.all_objects.count(), 1)

    def test_unique_together_phone_start_date(self):
        from django.db import IntegrityError

        ExcavatorOrder.objects.create(
            client_name="Client A",
            phone_number="+998906666666",
            lat=41.0,
            lon=69.0,
            start_date=date(2026, 1, 1),
        )
        with self.assertRaises(IntegrityError):
            ExcavatorOrder.objects.create(
                client_name="Client B",
                phone_number="+998906666666",
                lat=42.0,
                lon=70.0,
                start_date=date(2026, 1, 1),
            )

    def test_order_with_whouse(self):
        order = ExcavatorOrder.objects.create(
            client_name="Client",
            phone_number="+998907777777",
            lat=41.0,
            lon=69.0,
            whouse=self.whouse,
        )
        self.assertEqual(order.whouse, self.whouse)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ExcavatorSubOrderModelTest(TestCase):

    def setUp(self):
        from django.db.models.signals import post_save

        post_save.disconnect(dispatch_uid=None, sender=ExcavatorOrder)
        post_save.disconnect(dispatch_uid=None, sender=ExcavatorSubOrder)

        self.order = ExcavatorOrder.objects.create(
            client_name="Client",
            phone_number="+998908888888",
            lat=41.0,
            lon=69.0,
        )
        self.driver = Driver.objects.create(
            name="Test Driver",
            phone_number="+998909999999",
            type=Driver.Type.EXTERNAL,
        )
        self.transport = Transport.objects.create(
            name="Excavator 1",
            type=Transport.Type.EXTERNAL,
            car_type=Transport.CarType.EXCAVATOR,
            number="01A123AA",
        )

    def test_create_sub_order(self):
        sub = ExcavatorSubOrder.objects.create(
            parent=self.order,
            driver=self.driver,
            transport=self.transport,
        )
        self.assertEqual(sub.status, ExcavatorSubOrder.Status.NEW)
        self.assertEqual(sub.parent, self.order)
        self.assertEqual(sub.status_history, [])

    def test_sub_order_str(self):
        sub = ExcavatorSubOrder.objects.create(
            parent=self.order,
            driver=self.driver,
            transport=self.transport,
        )
        self.assertIn("ExcSubOrd-", str(sub))

    def test_unique_together_parent_driver(self):
        from django.db import IntegrityError

        ExcavatorSubOrder.objects.create(
            parent=self.order,
            driver=self.driver,
            transport=self.transport,
        )
        with self.assertRaises(IntegrityError):
            ExcavatorSubOrder.objects.create(
                parent=self.order,
                driver=self.driver,
                transport=self.transport,
            )

    def test_cascade_delete_with_parent(self):
        ExcavatorSubOrder.objects.create(
            parent=self.order,
            driver=self.driver,
            transport=self.transport,
        )
        self.order.delete(force=True) if hasattr(self.order.delete, '__code__') else ExcavatorOrder.all_objects.filter(id=self.order.id).delete()
        self.assertEqual(ExcavatorSubOrder.objects.count(), 0)


# ===================== API TESTS =====================


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ExcavatorOrderAPITest(APITestCase):

    def setUp(self):
        from django.db.models.signals import post_save

        post_save.disconnect(dispatch_uid=None, sender=ExcavatorOrder)
        post_save.disconnect(dispatch_uid=None, sender=ExcavatorSubOrder)

        self.client = APIClient()
        self.user = create_mock_user()

        self.auth_patcher = patch(
            "apps.common.auth.authentication.UnifiedJWTAuthentication.authenticate",
            return_value=(self.user, None),
        )
        self.perm_patcher = patch(
            "apps.common.permissions.HasDynamicPermission.has_permission",
            return_value=True,
        )
        self.mixin_patcher = patch(
            "apps.common.mixins.PermissionMetaMixin.get_permissions_meta",
            return_value={"can_access": True, "can_edit": True, "can_read": True},
        )
        self.auth_patcher.start()
        self.perm_patcher.start()
        self.mixin_patcher.start()

        self.whouse = Whouse.objects.create(name="API Test WH")
        self.order_data = {
            "client_name": "API Client",
            "phone_number": "+998901234567",
            "lat": 41.311,
            "lon": 69.279,
            "address": "Tashkent",
            "start_date": "2026-04-01",
            "end_date": "2026-04-10",
            "comment": "Test order",
        }

    def tearDown(self):
        self.auth_patcher.stop()
        self.perm_patcher.stop()
        self.mixin_patcher.stop()

    def _create_order(self, **overrides):
        data = {**self.order_data, **overrides}
        return ExcavatorOrder.objects.create(
            client_name=data["client_name"],
            phone_number=data["phone_number"],
            lat=data["lat"],
            lon=data["lon"],
            address=data.get("address"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            comment=data.get("comment"),
            whouse=data.get("whouse"),
        )

    def test_list_orders(self):
        self._create_order()
        self._create_order(phone_number="+998901111111", start_date="2026-05-01")
        response = self.client.get("/excavator-order/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_create_order(self):
        response = self.client.post(
            "/excavator-order/", self.order_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExcavatorOrder.objects.count(), 1)
        order = ExcavatorOrder.objects.first()
        self.assertEqual(order.client_name, "API Client")
        self.assertIsNotNone(order.display_id)

    def test_create_order_with_sub_orders(self):
        driver = Driver.objects.create(
            name="Driver 1", phone_number="+998911111111", type=Driver.Type.EXTERNAL
        )
        transport = Transport.objects.create(
            name="Exc 1",
            type=Transport.Type.EXTERNAL,
            car_type=Transport.CarType.EXCAVATOR,
            number="01B111BB",
        )
        data = {
            **self.order_data,
            "sub_orders": [
                {"driver": str(driver.id), "transport": str(transport.id)}
            ],
        }
        response = self.client.post("/excavator-order/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExcavatorSubOrder.objects.count(), 1)

    def test_retrieve_order(self):
        order = self._create_order()
        response = self.client.get(f"/excavator-order/{order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["client_name"], "API Client")

    def test_update_order(self):
        order = self._create_order()
        response = self.client.patch(
            f"/excavator-order/{order.id}/",
            {"client_name": "Updated Client"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.client_name, "Updated Client")

    def test_delete_order(self):
        order = self._create_order()
        response = self.client.delete(f"/excavator-order/{order.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExcavatorOrder.objects.count(), 0)

    def test_reject_order(self):
        order = self._create_order()
        driver = Driver.objects.create(
            name="D1", phone_number="+998912222222", type=Driver.Type.EXTERNAL
        )
        transport = Transport.objects.create(
            name="T1",
            type=Transport.Type.EXTERNAL,
            car_type=Transport.CarType.EXCAVATOR,
            number="02A111AA",
        )
        ExcavatorSubOrder.objects.create(
            parent=order, driver=driver, transport=transport
        )

        response = self.client.post(
            f"/excavator-order/{order.id}/reject/",
            {"status": "REJECTED", "timestamp": timezone.now().isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, ExcavatorOrder.Status.REJECTED)

        sub = order.sub_orders.first()
        self.assertEqual(sub.status, ExcavatorSubOrder.Status.REJECTED)

    def test_search_orders(self):
        self._create_order()
        response = self.client.get("/excavator-order/?search=API")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_status(self):
        self._create_order()
        order2 = self._create_order(
            phone_number="+998913333333", start_date="2026-06-01"
        )
        order2.status = ExcavatorOrder.Status.COMPLETED
        order2.save()

        response = self.client.get("/excavator-order/?status=NEW")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_payment_status(self):
        self._create_order()
        response = self.client.get("/excavator-order/?payment_status=PENDING")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_pagination(self):
        for i in range(15):
            self._create_order(
                phone_number=f"+99891000{i:04d}",
                start_date=date(2026, 1, 1) + timedelta(days=i),
            )
        response = self.client.get("/excavator-order/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)

        response = self.client.get("/excavator-order/?page=2")
        self.assertEqual(len(response.data["results"]), 5)


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ExcavatorSubOrderAPITest(APITestCase):

    def setUp(self):
        from django.db.models.signals import post_save

        post_save.disconnect(dispatch_uid=None, sender=ExcavatorOrder)
        post_save.disconnect(dispatch_uid=None, sender=ExcavatorSubOrder)

        self.client = APIClient()
        self.user = create_mock_user()

        self.auth_patcher = patch(
            "apps.common.auth.authentication.UnifiedJWTAuthentication.authenticate",
            return_value=(self.user, None),
        )
        self.perm_patcher = patch(
            "apps.common.permissions.HasDynamicPermission.has_permission",
            return_value=True,
        )
        self.mixin_patcher = patch(
            "apps.common.mixins.PermissionMetaMixin.get_permissions_meta",
            return_value={"can_access": True, "can_edit": True, "can_read": True},
        )
        self.qs_patcher = patch(
            "data.excavator.views.ExcavatorSubOrderViewSet.get_queryset",
        )

        self.auth_patcher.start()
        self.perm_patcher.start()
        self.mixin_patcher.start()
        mock_qs = self.qs_patcher.start()
        mock_qs.side_effect = lambda: ExcavatorSubOrder.objects.all()

        self.whouse = Whouse.objects.create(name="Sub API WH")
        self.order = ExcavatorOrder.objects.create(
            client_name="Parent Client",
            phone_number="+998920001111",
            lat=41.0,
            lon=69.0,
            whouse=self.whouse,
        )
        self.driver = Driver.objects.create(
            name="Sub Driver",
            phone_number="+998920002222",
            type=Driver.Type.EXTERNAL,
        )
        self.transport = Transport.objects.create(
            name="Sub Excavator",
            type=Transport.Type.EXTERNAL,
            car_type=Transport.CarType.EXCAVATOR,
            number="03A111AA",
        )

    def tearDown(self):
        self.auth_patcher.stop()
        self.perm_patcher.stop()
        self.mixin_patcher.stop()
        self.qs_patcher.stop()

    def _create_sub_order(self, **overrides):
        defaults = {
            "parent": self.order,
            "driver": self.driver,
            "transport": self.transport,
        }
        defaults.update(overrides)
        return ExcavatorSubOrder.objects.create(**defaults)

    def test_list_sub_orders(self):
        self._create_sub_order()
        response = self.client.get("/excavator-order/sub-orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_sub_order(self):
        sub = self._create_sub_order()
        response = self.client.get(f"/excavator-order/sub-orders/{sub.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["parent"]["client_name"], "Parent Client")

    @patch("data.excavator.views.ExcavatorSubOrderViewSet.get_queryset")
    def test_change_status(self, mock_extra_qs):
        # get_queryset is already patched in setUp, this additional patch is fine
        mock_extra_qs.return_value = ExcavatorSubOrder.objects.all()
        sub = self._create_sub_order()

        # Need to patch request attributes for change_status action
        with patch.object(
            ExcavatorSubOrder.objects, "all", return_value=ExcavatorSubOrder.objects.all()
        ):
            response = self.client.patch(
                f"/excavator-order/sub-orders/{sub.id}/change-status/",
                {
                    "status": "IN_PROGRESS",
                    "timestamp": timezone.now().isoformat(),
                },
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.status, ExcavatorSubOrder.Status.IN_PROGRESS)
        self.assertEqual(len(sub.status_history), 1)
        self.assertEqual(sub.status_history[0]["old_status"], "NEW")
        self.assertEqual(sub.status_history[0]["new_status"], "IN_PROGRESS")

    def test_change_status_updates_parent(self):
        """When all sub-orders have same status, parent should update."""
        sub = self._create_sub_order()

        response = self.client.patch(
            f"/excavator-order/sub-orders/{sub.id}/change-status/",
            {"status": "COMPLETED", "timestamp": timezone.now().isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ExcavatorOrder.Status.COMPLETED)

    def test_change_status_does_not_update_parent_with_mixed_statuses(self):
        """Parent stays unchanged if sub-orders have different statuses."""
        driver2 = Driver.objects.create(
            name="Driver 2", phone_number="+998920003333", type=Driver.Type.EXTERNAL
        )
        sub1 = self._create_sub_order()
        sub2 = self._create_sub_order(driver=driver2)

        self.client.patch(
            f"/excavator-order/sub-orders/{sub1.id}/change-status/",
            {"status": "COMPLETED", "timestamp": timezone.now().isoformat()},
            format="json",
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ExcavatorOrder.Status.NEW)

    def test_start_sub_order(self):
        sub = self._create_sub_order()
        response = self.client.post(
            f"/excavator-order/sub-orders/{sub.id}/start/",
            {"timestamp": timezone.now().isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.status, ExcavatorSubOrder.Status.IN_PROGRESS)

    def test_start_sub_order_with_sign(self):
        sub = self._create_sub_order()
        sign_file = File.objects.create(file="test_sign.png")

        response = self.client.post(
            f"/excavator-order/sub-orders/{sub.id}/start/",
            {
                "sign": str(sign_file.id),
                "timestamp": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.before_sign_id, sign_file.id)

    def test_finish_sub_order(self):
        sub = self._create_sub_order()
        sub.status = ExcavatorSubOrder.Status.IN_PROGRESS
        sub.save()

        response = self.client.post(
            f"/excavator-order/sub-orders/{sub.id}/finish/",
            {"timestamp": timezone.now().isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.status, ExcavatorSubOrder.Status.COMPLETED)

    def test_finish_sub_order_with_sign_and_files(self):
        sub = self._create_sub_order()
        sub.status = ExcavatorSubOrder.Status.IN_PROGRESS
        sub.save()

        sign_file = File.objects.create(file="after_sign.png")
        extra_file = File.objects.create(file="photo.jpg")

        response = self.client.post(
            f"/excavator-order/sub-orders/{sub.id}/finish/",
            {
                "sign": str(sign_file.id),
                "files": [str(extra_file.id)],
                "timestamp": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sub.refresh_from_db()
        self.assertEqual(sub.after_sign_id, sign_file.id)
        self.assertIn(extra_file, sub.after_files.all())

    def test_finish_all_updates_parent_to_completed(self):
        """When all sub-orders are finished, parent should become COMPLETED."""
        sub = self._create_sub_order()
        sub.status = ExcavatorSubOrder.Status.IN_PROGRESS
        sub.save()

        self.client.post(
            f"/excavator-order/sub-orders/{sub.id}/finish/",
            {"timestamp": timezone.now().isoformat()},
            format="json",
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, ExcavatorOrder.Status.COMPLETED)

    def test_filter_sub_orders_by_status(self):
        self._create_sub_order()
        response = self.client.get("/excavator-order/sub-orders/?status=NEW")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_in_progress_true(self):
        self._create_sub_order()
        response = self.client.get("/excavator-order/sub-orders/?in_progress=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_in_progress_false(self):
        sub = self._create_sub_order()
        sub.status = ExcavatorSubOrder.Status.COMPLETED
        sub.save()
        response = self.client.get("/excavator-order/sub-orders/?in_progress=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


# ===================== SERIALIZER TESTS =====================


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ExcavatorSerializerTest(TestCase):

    def setUp(self):
        from django.db.models.signals import post_save

        post_save.disconnect(dispatch_uid=None, sender=ExcavatorOrder)
        post_save.disconnect(dispatch_uid=None, sender=ExcavatorSubOrder)

        self.whouse = Whouse.objects.create(name="Serializer WH")
        self.order = ExcavatorOrder.objects.create(
            client_name="Ser Client",
            phone_number="+998930001111",
            lat=41.0,
            lon=69.0,
            whouse=self.whouse,
            start_date=date.today(),
        )

    def test_create_serializer_valid(self):
        from data.excavator.serializers import ExcavatorOrderCreateSerializer

        data = {
            "client_name": "New Client",
            "phone_number": "+998930002222",
            "lat": 41.5,
            "lon": 69.5,
            "start_date": "2026-04-01",
        }
        serializer = ExcavatorOrderCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_serializer_missing_required(self):
        from data.excavator.serializers import ExcavatorOrderCreateSerializer

        data = {"client_name": "Only Name"}
        serializer = ExcavatorOrderCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_change_status_serializer_valid(self):
        from data.excavator.serializers import ChangeStatusSerializer

        data = {"status": "IN_PROGRESS", "timestamp": timezone.now().isoformat()}
        serializer = ChangeStatusSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_change_status_serializer_invalid_status(self):
        from data.excavator.serializers import ChangeStatusSerializer

        data = {"status": "INVALID", "timestamp": timezone.now().isoformat()}
        serializer = ChangeStatusSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_start_order_serializer_valid(self):
        from data.excavator.serializers import StartOrderSerializer

        data = {"timestamp": timezone.now().isoformat()}
        serializer = StartOrderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_finish_order_serializer_valid(self):
        from data.excavator.serializers import FinishOrderSerializer

        data = {"timestamp": timezone.now().isoformat()}
        serializer = FinishOrderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_order_serializer_representation(self):
        from data.excavator.serializers import ExcavatorOrderSerializer

        serializer = ExcavatorOrderSerializer(self.order)
        data = serializer.data
        self.assertEqual(data["client_name"], "Ser Client")
        self.assertIsNotNone(data["whouse"])
        self.assertEqual(data["whouse"]["name"], "Serializer WH")


# ===================== TASK TESTS =====================


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ExcavatorTaskTest(TestCase):

    def setUp(self):
        from django.db.models.signals import post_save

        post_save.disconnect(dispatch_uid=None, sender=ExcavatorOrder)
        post_save.disconnect(dispatch_uid=None, sender=ExcavatorSubOrder)

    def test_expire_orders(self):
        from data.excavator.tasks import expire_excavator_orders

        order = ExcavatorOrder.objects.create(
            client_name="Expiring Client",
            phone_number="+998940001111",
            lat=41.0,
            lon=69.0,
            end_date=date.today() - timedelta(days=1),
        )
        sub = ExcavatorSubOrder.objects.create(
            parent=order,
            driver=Driver.objects.create(
                name="Exp Driver",
                phone_number="+998940002222",
                type=Driver.Type.EXTERNAL,
            ),
            transport=Transport.objects.create(
                name="Exp T",
                type=Transport.Type.EXTERNAL,
                car_type=Transport.CarType.EXCAVATOR,
                number="04A111AA",
            ),
        )

        expire_excavator_orders()

        order.refresh_from_db()
        sub.refresh_from_db()
        self.assertEqual(order.status, ExcavatorOrder.Status.EXPIRED)
        self.assertEqual(sub.status, ExcavatorSubOrder.Status.EXPIRED)

    def test_expire_does_not_affect_completed_orders(self):
        from data.excavator.tasks import expire_excavator_orders

        order = ExcavatorOrder.objects.create(
            client_name="Completed Client",
            phone_number="+998940003333",
            lat=41.0,
            lon=69.0,
            end_date=date.today() - timedelta(days=1),
            status=ExcavatorOrder.Status.COMPLETED,
        )

        expire_excavator_orders()

        order.refresh_from_db()
        self.assertEqual(order.status, ExcavatorOrder.Status.COMPLETED)

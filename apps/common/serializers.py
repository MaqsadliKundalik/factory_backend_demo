from rest_framework import serializers
from .models import UserPermissions
from django.contrib.contenttypes.models import ContentType

class UserPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissions
        fields = [
            "crud_whouse_manager", "read_whouse_manager",
            "crud_factory_operator", "read_factory_operator",
            "crud_driver", "read_driver",
            "crud_guard", "read_guard",
            "crud_product", "read_product",
            "crud_transport", "read_transport",
            "crud_client", "read_client",
            "read_whouse"
        ]

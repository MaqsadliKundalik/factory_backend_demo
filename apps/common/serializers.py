from rest_framework import serializers
from .models import UserPermissions
from django.contrib.contenttypes.models import ContentType

class UserPermissionsSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPermissions
        fields = [
            "id", "content_type", "object_id", "content_type_name",
            "crud_whouse_manager", "read_whouse_manager",
            "crud_factory_operator", "read_factory_operator",
            "crud_driver", "read_driver",
            "crud_guard", "read_guard",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_content_type_name(self, obj):
        return obj.content_type.model

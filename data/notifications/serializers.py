from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'from_role', 'to_role', 'to_user_id', 'is_read']
        read_only_fields = ['id']
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(PermissionMetaMixin, ModelViewSet):
    serializer_class = NotificationSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['to_role', 'is_read', 'from_role']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
            
        role = getattr(user, 'role', None) or self.request.auth.get('role')
        if not role:
            return Notification.objects.none()
            
        return Notification.objects.filter(to_role=role)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        role = getattr(request.user, 'role', None) or request.auth.get('role')
        if not role:
            return Response({"error": "Role not found"}, status=status.HTTP_400_BAD_REQUEST)
            
        Notification.objects.filter(to_role=role, is_read=False).update(is_read=True)
        return Response({"message": "All notifications marked as read"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)

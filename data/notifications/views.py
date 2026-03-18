from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.mixins import DateFilterSchemaMixin
from apps.common.filters import BaseDateFilterSet
from .models import Notification
from .serializers import NotificationSerializer



def _get_role(request):
    """Auth qilingan userning rolini oladi (FactoryUser yoki Driver)."""
    return getattr(request.user, 'role', None) or (
        request.auth.get('role') if isinstance(request.auth, dict) else None
    )



class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100



class NotificationFilter(BaseDateFilterSet):
    class Meta:
        model = Notification
        fields = ['is_read', 'from_role']



class NotificationViewSet(
    DateFilterSchemaMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NotificationFilter
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()

        role = _get_role(self.request)
        if not role:
            return Notification.objects.none()

        user_id = str(self.request.user.id)
        # Faqat menga yuborilgan (to_user_id=mening_id) yoki hammaga yuborilgan (to_user_id=None)
        from django.db.models import Q
        return Notification.objects.filter(
            to_role=role
        ).filter(
            Q(to_user_id__isnull=True) | Q(to_user_id=user_id)
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                },
            )
        },
    )
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        role = _get_role(request)
        if not role:
            return Response({"error": "Роль не определена"}, status=status.HTTP_400_BAD_REQUEST)

        from django.db.models import Q
        user_id = str(request.user.id)
        updated = Notification.objects.filter(
            to_role=role, is_read=False
        ).filter(
            Q(to_user_id__isnull=True) | Q(to_user_id=user_id)
        ).update(is_read=True)
        return Response(
            {"message": "Все уведомления отмечены как прочитанные", "count": updated},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
        responses={200: NotificationSerializer()},
    )
    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'unread_count': openapi.Schema(type=openapi.TYPE_INTEGER, example=3)},
            )
        },
    )
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        role = _get_role(request)
        if not role:
            return Response({"unread_count": 0})
        from django.db.models import Q
        user_id = str(request.user.id)
        count = Notification.objects.filter(
            to_role=role, is_read=False
        ).filter(
            Q(to_user_id__isnull=True) | Q(to_user_id=user_id)
        ).count()
        return Response({"unread_count": count})

from rest_framework.viewsets import ModelViewSet
from .models import Transport
from .serializers import TransportSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.filters import BaseDateFilterSet
from apps.common.mixins import PermissionMetaMixin
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TransportFilter(BaseDateFilterSet):
    class Meta:
        model = Transport
        fields = ['whouse', 'created_at', 'updated_at']

class TransportViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="TRANSPORTS_PAGE", read_perm="TRANSPORTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TransportFilter
    search_fields = ['name', 'number']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Transport.objects.none()

        whouses = user.whouses.all()
        return Transport.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)
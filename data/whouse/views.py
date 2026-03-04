from rest_framework.viewsets import ModelViewSet
from .models import Whouse
from .serializers import WhouseGetSerializer, WhouseCreateUpdateSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from apps.common.filters import BaseDateFilterSet

class WhouseFilter(BaseDateFilterSet):
    class Meta:
        model = Whouse
        fields = ['name', 'start_date', 'end_date']

class WhouseViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = Whouse.objects.all()
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(read_perm="MAIN_PAGE", crud_perm="MAIN_PAGE")]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = WhouseFilter
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return WhouseGetSerializer
        return WhouseCreateUpdateSerializer

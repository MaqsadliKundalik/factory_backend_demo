from rest_framework.viewsets import ModelViewSet
from .models import Whouse
from .serializers import WhouseGetSerializer, WhouseCreateUpdateSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin

class WhouseViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = Whouse.objects.all()
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(read_perm="MAIN_PAGE", crud_perm="MAIN_PAGE")]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return WhouseGetSerializer
        return WhouseCreateUpdateSerializer

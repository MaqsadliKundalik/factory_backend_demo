from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from apps.whouse.models import Whouse
from apps.whouse.serializers import WhouseGetSerializer, WhouseCreateUpdateSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class WhouseViewSet(ModelViewSet):
    queryset = Whouse.objects.all()
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse", read_perm="read_whouse")]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return WhouseGetSerializer
        return WhouseCreateUpdateSerializer

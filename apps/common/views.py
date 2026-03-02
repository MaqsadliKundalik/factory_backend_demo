from rest_framework.viewsets import ModelViewSet
from .models import UserPermissions
from .serializers import UserPermissionsSerializer
from .auth.authentication import UnifiedJWTAuthentication
from .permissions import HasDynamicPermission

from .mixins import PermissionMetaMixin

class UserPermissionsViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = UserPermissions.objects.all()
    serializer_class = UserPermissionsSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse_manager")]

    def get_queryset(self):
        return super().get_queryset()

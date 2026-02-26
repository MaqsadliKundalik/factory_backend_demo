from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.whouse_manager.models import WhouseManager
from apps.whouse_manager.serializers import WhouseManagerSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class WhouseManagerListCreateAPIView(ListCreateAPIView):
    queryset = WhouseManager.objects.all()
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse_manager", read_perm="read_whouse_manager")]

class WhouseManagerRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = WhouseManager.objects.all()
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse_manager", read_perm="read_whouse_manager")]

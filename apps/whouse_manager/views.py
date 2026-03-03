from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from data.users.models import FactoryUser
from apps.whouse_manager.serializers.whouse_manager import WhouseManagerSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class WhouseManagerListCreateAPIView(ListCreateAPIView):
    queryset = FactoryUser.objects.filter(role='manager')
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse_manager", read_perm="read_whouse_manager")]

class WhouseManagerRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = FactoryUser.objects.filter(role='manager')
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse_manager", read_perm="read_whouse_manager")]

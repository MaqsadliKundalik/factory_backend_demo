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

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        whouses = user.whouses.all()
        return FactoryUser.objects.filter(role='manager', whouses__in=whouses).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouses=[whouse_id])
        else:
            whouse = user.whouses.first()
            serializer.save(whouses=[whouse])

class WhouseManagerRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = FactoryUser.objects.filter(role='manager')
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_whouse_manager", read_perm="read_whouse_manager")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        whouses = user.whouses.all()
        return FactoryUser.objects.filter(role='manager', whouses__in=whouses).distinct()

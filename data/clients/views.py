from rest_framework.viewsets import ModelViewSet
from .models import Client
from .serializers import ClientSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_client", read_perm="read_client")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Client.objects.none()

        if hasattr(user, 'whouses'):
            return Client.objects.filter(whouse__in=user.whouses.all())
        return Client.objects.filter(whouse=user.whouse)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
            serializer.save(whouse=whouse)

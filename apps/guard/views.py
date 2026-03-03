from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from data.users.models import FactoryUser
from apps.guard.serializers import GuardSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class GuardListCreateAPIView(ListCreateAPIView):
    queryset = FactoryUser.objects.filter(role='guard')
    serializer_class = GuardSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_guard", read_perm="read_guard")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        qs = FactoryUser.objects.filter(role='guard')
        if user.whouse:
            return qs.filter(whouse=user.whouse)
        return qs
        
    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            serializer.save(whouse=user.whouse)

class GuardRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = FactoryUser.objects.filter(role='guard')
    serializer_class = GuardSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_guard", read_perm="read_guard")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        qs = FactoryUser.objects.filter(role='guard')
        if user.whouse:
            return qs.filter(whouse=user.whouse)
        return qs

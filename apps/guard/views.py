from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.guard.models import Guard
from apps.guard.serializers import GuardSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class GuardListCreateAPIView(ListCreateAPIView):
    queryset = Guard.objects.all()
    serializer_class = GuardSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_guard", read_perm="read_guard")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Guard.objects.none()

        if hasattr(user, 'whouses'):
            return Guard.objects.filter(whouse__in=user.whouses.all())
        return Guard.objects.filter(whouse=user.whouse)
        
    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
            serializer.save(whouse=whouse)

class GuardRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Guard.objects.all()
    serializer_class = GuardSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_guard", read_perm="read_guard")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Guard.objects.none()

        if hasattr(user, 'whouses'):
            return Guard.objects.filter(whouse__in=user.whouses.all())
        return Guard.objects.filter(whouse=user.whouse)

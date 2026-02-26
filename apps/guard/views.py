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
        return Guard.objects.filter(whouse=user.whouse)
        
    def perform_create(self, serializer):
        serializer.save(whouse=self.request.user.whouse)

class GuardRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Guard.objects.all()
    serializer_class = GuardSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_guard", read_perm="read_guard")]

    def get_queryset(self):
        user = self.request.user
        return Guard.objects.filter(whouse=user.whouse)

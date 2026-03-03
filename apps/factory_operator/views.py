from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from data.users.models import FactoryUser
from apps.factory_operator.serializers.factory_operator import FactoryOperatorSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

class FactoryOperatorListCreateAPIView(ListCreateAPIView):
    queryset = FactoryUser.objects.filter(role='operator')
    serializer_class = FactoryOperatorSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_factory_operator", read_perm="read_factory_operator")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        whouses = user.whouses.all()
        return FactoryUser.objects.filter(role='operator', whouses__in=whouses).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouses=[whouse_id])
        else:
            whouse = user.whouses.first()
            serializer.save(whouses=[whouse])

class FactoryOperatorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = FactoryUser.objects.filter(role='operator')
    serializer_class = FactoryOperatorSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_factory_operator", read_perm="read_factory_operator")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        whouses = user.whouses.all()
        return FactoryUser.objects.filter(role='operator', whouses__in=whouses).distinct()

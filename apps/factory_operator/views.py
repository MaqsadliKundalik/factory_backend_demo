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

class FactoryOperatorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = FactoryUser.objects.filter(role='operator')
    serializer_class = FactoryOperatorSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_factory_operator", read_perm="read_factory_operator")]

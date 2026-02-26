from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from apps.factory_operator.models import FactoryOperator
from apps.factory_operator.serializers import FactoryOperatorSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

# Create your views here.

class FactoryOperatorListCreateAPIView(ListCreateAPIView):
    queryset = FactoryOperator.objects.all()
    serializer_class = FactoryOperatorSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_factory_operator", read_perm="read_factory_operator")]

class FactoryOperatorRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = FactoryOperator.objects.all()
    serializer_class = FactoryOperatorSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_factory_operator", read_perm="read_factory_operator")]

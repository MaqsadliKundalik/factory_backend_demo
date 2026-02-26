from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import ProductType
from .serializers import ProductTypeSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
# Create your views here.

class ProductTypeListCreateAPIView(ListCreateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product_type", read_perm="read_product_type")]

    def get_queryset(self):
        user = self.request.user
        return ProductType.objects.filter(whouse=user.whouse)

    def perform_create(self, serializer):
        serializer.save(whouse=self.request.user.whouse)

class ProductTypeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product_type", read_perm="read_product_type")]

    def get_queryset(self):
        user = self.request.user
        return ProductType.objects.filter(whouse=user.whouse)


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
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return ProductType.objects.none()

        if hasattr(user, 'whouses'):
            return ProductType.objects.filter(whouse__in=user.whouses.all())
        return ProductType.objects.filter(whouse=user.whouse)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            # Default to first whouse for managers, or the only whouse for others
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
            serializer.save(whouse=whouse)

class ProductTypeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product_type", read_perm="read_product_type")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return ProductType.objects.none()

        if hasattr(user, 'whouses'):
            return ProductType.objects.filter(whouse__in=user.whouses.all())
        return ProductType.objects.filter(whouse=user.whouse)


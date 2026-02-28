from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission

from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory
from .serializers import (
    ProductTypeSerializer, ProductUnitSerializer, ProductSerializer, 
    WhouseProductsSerializer, WhouseProductsHistorySerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class WhouseProductsHistoryViewSet(ReadOnlyModelViewSet):
    queryset = WhouseProductsHistory.objects.all()
    serializer_class = WhouseProductsHistorySerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product", read_perm="read_product")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['whouse_product', 'whouse', 'product', 'status']
    search_fields = ['product__name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return WhouseProductsHistory.objects.none()

        if hasattr(user, 'whouses'):
            return WhouseProductsHistory.objects.filter(whouse__in=user.whouses.all())
        return WhouseProductsHistory.objects.filter(whouse=user.whouse)


class ProductTypeViewSet(ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product", read_perm="read_product")]

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
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
            serializer.save(whouse=whouse)

class ProductUnitViewSet(ModelViewSet):
    queryset = ProductUnit.objects.all()
    serializer_class = ProductUnitSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product", read_perm="read_product")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return ProductUnit.objects.none()

        if hasattr(user, 'whouses'):
            return ProductUnit.objects.filter(whouse__in=user.whouses.all())
        return ProductUnit.objects.filter(whouse=user.whouse)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
            serializer.save(whouse=whouse)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product", read_perm="read_product")]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):

        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Product.objects.none()

        if hasattr(user, 'whouses'):
            return Product.objects.filter(whouse__in=user.whouses.all())
        return Product.objects.filter(whouse=user.whouse)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        # Warehouse handling is also in Serializer.create for Product
        serializer.save()

    filter_backends = [SearchFilter]
    search_fields = ['name']

class WhouseProductsViewSet(ModelViewSet):
    queryset = WhouseProducts.objects.all()
    serializer_class = WhouseProductsSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="crud_product", read_perm="read_product")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['whouse', 'product', 'status', 'created_at', 'updated_at']
    search_fields = ['product__name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return WhouseProducts.objects.none()

        if hasattr(user, 'whouses'):
            return WhouseProducts.objects.filter(whouse__in=user.whouses.all())
        return WhouseProducts.objects.filter(whouse=user.whouse)

    def perform_create(self, serializer):
        user = self.request.user
        whouse = user.whouses.first() if hasattr(user, 'whouses') else user.whouse
        serializer.save(whouse=whouse)

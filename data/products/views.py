from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin
from data.notifications.models import Notification
from drf_yasg.utils import swagger_auto_schema

from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory
from .serializers import (
    ProductTypeSerializer, ProductUnitSerializer, ProductSerializer, 
    WhouseProductsSerializer, WhouseProductsHistorySerializer,  SelectProductSerializer
)



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class WhouseProductsHistoryViewSet(PermissionMetaMixin, ReadOnlyModelViewSet):
    queryset = WhouseProductsHistory.objects.all()
    serializer_class = WhouseProductsHistorySerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['whouse_product', 'whouse', 'product', 'product_type', 'status']
    search_fields = ['product__name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return WhouseProductsHistory.objects.none()

        whouses = user.whouses.all()
        return WhouseProductsHistory.objects.filter(whouse__in=whouses)


class ProductTypeViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['whouse']
    search_fields = ['name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return ProductType.objects.none()

        whouses = user.whouses.all()
        return ProductType.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)

class ProductUnitViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ProductUnit.objects.all()
    serializer_class = ProductUnitSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return ProductUnit.objects.none()

        whouses = user.whouses.all()
        return ProductUnit.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        if whouse_id:
            serializer.save(whouse_id=whouse_id)
        else:
            whouse = user.whouses.first()
            serializer.save(whouse=whouse)

class ProductViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):

        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return Product.objects.none()

        whouses = user.whouses.all()
        return Product.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        # Warehouse handling is also in Serializer.create for Product

        serializer.save()

    filter_backends = [SearchFilter]
    search_fields = ['name']

    @swagger_auto_schema(
        operation_summary="Select products (id and name only)",
        responses={200: SelectProductSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], pagination_class=None)
    def select(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)
        
        whouses = user.whouses.all()
        queryset = Product.objects.filter(whouse__in=whouses)
        
        # Apply search if provided
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        data = queryset.values('id', 'name')
        return Response(list(data))

class WhouseProductsViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = WhouseProducts.objects.all()
    serializer_class = WhouseProductsSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['whouse', 'product', 'status', 'created_at', 'updated_at']
    search_fields = ['product__name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return WhouseProducts.objects.none()

        whouses = user.whouses.all()
        return WhouseProducts.objects.filter(whouse__in=whouses)

    def perform_create(self, serializer):
        user = self.request.user
        whouse = user.whouses.first()
        serializer.save(whouse=whouse)

from rest_framework import mixins, viewsets

class WhouseProductsActionViewSet(PermissionMetaMixin, viewsets.GenericViewSet):
    queryset = WhouseProducts.objects.all()
    serializer_class = WhouseProductsSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
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

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'confirmed'
        instance.save()
        
        Notification.objects.create(
            to_role='guard',
            from_role='whouse_manager',
            title='Product confirmed',
            message=f'Product {instance.product.name} has been confirmed by manager',
        )
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'rejected'
        instance.save()
        
        Notification.objects.create(
            to_role='guard',
            from_role='whouse_manager',
            title='Product rejected',
            message=f'Product {instance.product.name} has been rejected by manager',
        )
        return Response({'status': 'rejected'})



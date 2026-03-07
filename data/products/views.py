from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from apps.common.mixins import PermissionMetaMixin, DateFilterSchemaMixin
from data.notifications.models import Notification
from drf_yasg.utils import swagger_auto_schema

from .models import ProductType, ProductUnit, Product, WhouseProducts, WhouseProductsHistory, ProductItem
from .serializers import (
    ProductTypeSerializer, ProductUnitSerializer, ProductSerializer, ProductAndItemCreateSerializer,
    WhouseProductsSerializer, WhouseProductsHistorySerializer,  SelectProductSerializer, ProductItemSerializer
)



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class WhouseProductsFilter(BaseDateFilterSet):
    class Meta:
        model = WhouseProducts
        fields = ['whouse', 'product', 'status', 'created_at', 'updated_at']

class WhouseProductsHistoryFilter(BaseDateFilterSet):
    class Meta:
        model = WhouseProductsHistory
        fields = ['whouse', 'product', 'status']

class ProductItemFilter(BaseDateFilterSet):
    class Meta:
        model = ProductItem
        fields = ['product', 'type', 'unit']

class ProductFilter(BaseDateFilterSet):
    class Meta:
        model = Product
        fields = ['whouse', 'unit']

class ProductTypeFilter(BaseDateFilterSet):
    class Meta:
        model = ProductType
        fields = ['whouse']

class ProductUnitFilter(BaseDateFilterSet):
    class Meta:
        model = ProductUnit
        fields = ['whouse']

class WhouseProductsHistoryViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ReadOnlyModelViewSet):
    queryset = WhouseProductsHistory.objects.all()
    serializer_class = WhouseProductsHistorySerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="WHEREHOUSES_PAGE", read_perm="WHEREHOUSES_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = WhouseProductsHistoryFilter
    search_fields = ['product__name']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return WhouseProductsHistory.objects.none()

        whouses = user.whouses.all()
        queryset = WhouseProductsHistory.objects.filter(whouse__in=whouses)

        is_ready = self.request.query_params.get('is_ready_product')
        if is_ready is not None:
            if is_ready.lower() == 'true':
                queryset = queryset.filter(product__items__isnull=False).distinct()
            elif is_ready.lower() == 'false':
                queryset = queryset.filter(product__items__isnull=True)

        return queryset

    @swagger_auto_schema(manual_parameters=DATE_FILTER_PARAMS + [IS_READY_PRODUCT_PARAM])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductTypeViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductTypeFilter
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

class ProductUnitViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = ProductUnit.objects.all()
    serializer_class = ProductUnitSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductUnitFilter
    search_fields = ['name']

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

class ProductItemViewSet(PermissionMetaMixin, ModelViewSet):
    queryset = ProductItem.objects.all()
    serializer_class = ProductItemSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="READY_PRODUCTS_PAGE", read_perm="READY_PRODUCTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductItemFilter
    search_fields = ['name']

class ProductViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
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
        queryset = Product.objects.filter(whouse__in=whouses)

        is_ready = self.request.query_params.get('is_ready_product')
        if is_ready is not None:
            if is_ready.lower() == 'true':
                queryset = queryset.filter(items__isnull=False).distinct()
            elif is_ready.lower() == 'false':
                queryset = queryset.filter(items__isnull=True)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        whouse_id = self.request.data.get('whouse')
        # Warehouse handling is also in Serializer.create for Product

        serializer.save()

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name']

    @swagger_auto_schema(manual_parameters=DATE_FILTER_PARAMS + [IS_READY_PRODUCT_PARAM])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
        is_ready = self.request.query_params.get('is_ready_product')
        if is_ready is not None:
            if is_ready.lower() == 'true':
                queryset = queryset.filter(items__isnull=False).distinct()
            elif is_ready.lower() == 'false':
                queryset = queryset.filter(items__isnull=True)

        # Apply search if provided
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        data = queryset.values('id', 'name')
        return Response(list(data))
class WhouseProductsViewSet(DateFilterSchemaMixin, PermissionMetaMixin, ModelViewSet):
    queryset = WhouseProducts.objects.all()
    serializer_class = WhouseProductsSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = WhouseProductsFilter
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
    filterset_class = WhouseProductsFilter
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


class ProductAndItemCreateView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [HasDynamicPermission(crud_perm="PRODUCTS_PAGE", read_perm="PRODUCTS_PAGE")]

    @swagger_auto_schema(
        operation_summary="Create product and items",
        request_body=ProductAndItemCreateSerializer,
        responses={201: ProductSerializer}
    )
    @transaction.atomic
    def post(self, request):
        serializer = ProductAndItemCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
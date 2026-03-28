from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .serializers import (
    FactoryUserSerializer,
    FactoryUserResetpasswordSerializer,
    SelectFactoryUserSerializer,
)
from data.users.models import FactoryUser
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import HasDynamicPermission
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import DateFilterSchemaMixin
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.common.filters import BaseDateFilterSet
import logging

logger = logging.getLogger(__name__)

TRANSPORT_FILTER_PARAMS = [
    openapi.Parameter(
        "role",
        openapi.IN_QUERY,
        description="Filter by role",
        type=openapi.TYPE_STRING,
        required=False,
    ),
]

class UserListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class FactoryUserResetPasswordViewSet(ViewSet):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="USERS_PAGE", read_perm="USERS_PAGE")
    ]
    serializer_class = FactoryUserResetpasswordSerializer

    @swagger_auto_schema(
        operation_summary="Reset password",
        request_body=FactoryUserResetpasswordSerializer,
        responses={200: FactoryUserResetpasswordSerializer()},
    )
    def reset_password(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = FactoryUser.objects.get(id=serializer.validated_data["id"])
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                return Response(
                    {"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FactoryUserFilter(BaseDateFilterSet):
    class Meta:
        model = FactoryUser
        fields = ["whouses", "role", "is_active"]


class FactoryUserViewSet(DateFilterSchemaMixin, ModelViewSet):
    queryset = FactoryUser.objects.all().order_by("-created_at")
    serializer_class = FactoryUserSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="USERS_PAGE", read_perm="USERS_PAGE")
    ]
    pagination_class = UserListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FactoryUserFilter
    search_fields = ["name", "phone_number"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return FactoryUser.objects.none()

        queryset = super().get_queryset()

        # Superuser sees all, others see users in their warehouses
        if not user.is_superuser:
            queryset = queryset.filter(whouses__in=user.whouses.all()).distinct()

        whouse_id = self.request.query_params.get("whouse")
        if whouse_id:
            queryset = queryset.filter(whouses__id=whouse_id)
        return queryset


class UserSelectView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [
        HasDynamicPermission(crud_perm="USERS_PAGE", read_perm="USERS_PAGE")
    ]

    @swagger_auto_schema(
        operation_summary="Select users (id and name only)",
        responses={200: SelectFactoryUserSerializer(many=True)},
        manual_parameters=TRANSPORT_FILTER_PARAMS,
    )
    def get(self, request):
        role = request.query_params.get("role")

        user = (
            self.request.driver
            or self.request.guard
            or self.request.operator
            or self.request.manager
        )
        if not user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)

    
        queryset = FactoryUser.objects.all()

        if role:
            queryset = queryset.filter(role=role)

        data = queryset.values("id", "name", "role")
        return Response(list(data))

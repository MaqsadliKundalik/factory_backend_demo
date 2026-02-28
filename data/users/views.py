from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.shortcuts import get_object_or_404
from itertools import chain
from apps.drivers.models import Driver
from apps.guard.models import Guard
from apps.factory_operator.models import FactoryOperator
from apps.whouse_manager.models import WhouseManager
from .serializers import UnifiedUserSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class UserListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UnifiedUserViewSet(ViewSet):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = UserListPagination
    serializer_class = UnifiedUserSerializer

    def _get_all_users_queryset(self, whouse_id=None):
        managers = WhouseManager.objects.all().order_by('-created_at')
        operators = FactoryOperator.objects.all().order_by('-created_at')
        drivers = Driver.objects.all().order_by('-created_at')
        guards = Guard.objects.all().order_by('-created_at')

        if whouse_id:
            managers = managers.filter(whouses__id=whouse_id)
            operators = operators.filter(whouse__id=whouse_id)
            drivers = drivers.filter(whouse__id=whouse_id)
            guards = guards.filter(whouse__id=whouse_id)

        return sorted(
            chain(managers, operators, drivers, guards),
            key=lambda x: x.created_at,
            reverse=True
        )

    def _get_instance(self, pk):
        for model in [WhouseManager, FactoryOperator, Driver, Guard]:
            try:
                instance = model.objects.filter(id=pk).first()
                if instance:
                    return instance
            except Exception as e:
                logger.error(f"Error finding user {pk} in {model.__name__}: {str(e)}")
                continue
        return None

    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="Returns a paginated list of all users from all roles.",
        manual_parameters=[
            openapi.Parameter('whouse', openapi.IN_QUERY, description="Filter by Warehouse ID", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        ],
        responses={200: UnifiedUserSerializer(many=True)}
    )
    def list(self, request):
        whouse_id = request.query_params.get('whouse')
        combined_users = self._get_all_users_queryset(whouse_id)
        
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(combined_users, request, view=self)
        
        serializer = UnifiedUserSerializer(paginated_users, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        request_body=UnifiedUserSerializer,
        responses={201: UnifiedUserSerializer()}
    )
    def create(self, request):
        serializer = UnifiedUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Retrieve a user",
        responses={200: UnifiedUserSerializer()}
    )
    def retrieve(self, request, pk=None):
        try:
            instance = self._get_instance(pk)
            if not instance:
                return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
            serializer = UnifiedUserSerializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.exception("Error in UnifiedUserViewSet.retrieve")
            return Response({"detail": f"Serialization xatoligi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Update a user",
        request_body=UnifiedUserSerializer,
        responses={200: UnifiedUserSerializer()}
    )
    def update(self, request, pk=None):
        try:
            instance = self._get_instance(pk)
            if not instance:
                return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
            serializer = UnifiedUserSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Update xatoligi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Partial update a user",
        request_body=UnifiedUserSerializer,
        responses={200: UnifiedUserSerializer()}
    )
    def partial_update(self, request, pk=None):
        try:
            instance = self._get_instance(pk)
            if not instance:
                return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
            serializer = UnifiedUserSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Partial update xatoligi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        responses={204: "Successfully deleted"}
    )
    def destroy(self, request, pk=None):
        try:
            instance = self._get_instance(pk)
            if not instance:
                return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": f"O'chirishda xatolik: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

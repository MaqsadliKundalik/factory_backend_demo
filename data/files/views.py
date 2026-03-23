from django.http import FileResponse
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.common.filters import BaseDateFilterSet, DATE_FILTER_PARAMS

from .models import File, Documents
from .serializers import FileSerializer, DocumentsSerializer


class FileCreateView(generics.CreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]


class FileDownloadView(generics.RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        return FileResponse(
            file_obj.file.open(), as_attachment=True, filename=file_obj.file.name
        )


class DocumentsFilter(BaseDateFilterSet):
    class Meta:
        model = Documents
        fields = ["type", "object_id"]


DOCUMENTS_FILTER_PARAMS = DATE_FILTER_PARAMS + [
    openapi.Parameter(
        "type",
        openapi.IN_QUERY,
        description="Hujjat turi: DRIVER, TRANSPORT, SUPPLIER, CLIENT, SUBORDER, PRODUCT, OTHER",
        type=openapi.TYPE_STRING,
        required=False,
    ),
    openapi.Parameter(
        "object_id",
        openapi.IN_QUERY,
        description="Bog'liq obyekt UUID si",
        type=openapi.TYPE_STRING,
        format=openapi.FORMAT_UUID,
        required=False,
    ),
]


class DocumentsViewSet(viewsets.ModelViewSet):
    queryset = Documents.objects.all()
    serializer_class = DocumentsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = DocumentsFilter

    @swagger_auto_schema(manual_parameters=DOCUMENTS_FILTER_PARAMS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

from django.http import FileResponse
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.filters import BaseDateFilterSet
from apps.common.mixins import DateFilterSchemaMixin
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
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        return FileResponse(file_obj.file.open(), as_attachment=True, filename=file_obj.file.name)


class DocumentsFilter(BaseDateFilterSet):
    class Meta:
        model = Documents
        fields = ['type', 'object_id']


class DocumentsViewSet(DateFilterSchemaMixin, viewsets.ModelViewSet):
    queryset = Documents.objects.all()
    serializer_class = DocumentsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = DocumentsFilter

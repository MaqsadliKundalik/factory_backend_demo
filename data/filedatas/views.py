from django.http import FileResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import File
from .serializers import FileSerializer

class FileCreateView(generics.CreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FileDownloadView(generics.RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        return FileResponse(file_obj.file.open(), as_attachment=True, filename=file_obj.file.name)

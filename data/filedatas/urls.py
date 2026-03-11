from django.urls import path, Router
from .views import FileCreateView, FileDownloadView, DocumentsViewSet

router = Router()
router.register(r'documents', DocumentsViewSet, basename='documents')

urlpatterns = [
    path('upload/', FileCreateView.as_view(), name='file-upload'),
    path('download/<uuid:id>/', FileDownloadView.as_view(), name='file-download'),
    *router.urls,
]
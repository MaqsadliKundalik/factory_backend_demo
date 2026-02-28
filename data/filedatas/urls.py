from django.urls import path
from .views import FileCreateView, FileDownloadView

urlpatterns = [
    path('upload/', FileCreateView.as_view(), name='file-upload'),
    path('download/<uuid:id>/', FileDownloadView.as_view(), name='file-download'),
]
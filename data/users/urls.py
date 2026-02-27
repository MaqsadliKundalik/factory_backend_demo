from django.urls import path
from .views import UnifiedUserListView

urlpatterns = [
    path('', UnifiedUserListView.as_view(), name='unified-user-list'),
]

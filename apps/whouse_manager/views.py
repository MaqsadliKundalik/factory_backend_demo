from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from apps.whouse_manager.models import WhouseManager
from apps.whouse_manager.serializers import WhouseManagerSerializer
from apps.common.auth.authentication import UnifiedJWTAuthentication
from apps.common.permissions import IsWhouseManager

# Create your views here.

class WhouseManagerListCreateAPIView(ListCreateAPIView):
    queryset = WhouseManager.objects.all()
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsWhouseManager]

class WhouseManagerRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = WhouseManager.objects.all()
    serializer_class = WhouseManagerSerializer
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsWhouseManager]

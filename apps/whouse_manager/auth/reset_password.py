from rest_framework.request import HttpRequest, Request
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.whouse_manager.serializers.auth import ChangePasswordSerializer
from apps.whouse_manager.auth.authentication import WhouseManagerJWTAuthentication

class ChangePasswordAPIView(APIView):
    authentication_classes = [WhouseManagerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Whouse Manager Auth"],
        operation_summary="Change Password",
        request_body=ChangePasswordSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"whouse_manager": request.user}
        )
        serializer.is_valid(raise_exception=True)

        manager = serializer.save()
        
        # Invalidate old sessions
        from apps.session.models import WhouseManagerSession
        WhouseManagerSession.objects.filter(whouse_manager=manager).delete()
        
        # Create new session
        new_session = manager.new_session()
        refresh = new_session.token
        
        return Response({
            "detail": "Parol muvaffaqiyatli o'zgartirildi.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

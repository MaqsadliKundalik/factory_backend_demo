from rest_framework.request import HttpRequest, Request
from rest_framework.exceptions import NotAcceptable
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema  

from apps.factory_operator.serializers.auth import ChangePasswordSerializer
from apps.factory_operator.auth.authentication import FactoryOperatorJWTAuthentication

class ChangePasswordAPIView(APIView):
    authentication_classes = [FactoryOperatorJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Factory Operator Auth"],
        operation_summary="Change Password",
        request_body=ChangePasswordSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"whouse_manager": request.user}
        )
        serializer.is_valid(raise_exception=True)

        operator = serializer.save()
        
        # Invalidate old sessions
        from apps.session.models import FactoryOperatorSession
        FactoryOperatorSession.objects.filter(operator=operator).delete()
        
        # Create new session
        new_session = operator.new_session()
        refresh = new_session.token
        
        return Response({
            "detail": "Parol muvaffaqiyatli o'zgartirildi.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

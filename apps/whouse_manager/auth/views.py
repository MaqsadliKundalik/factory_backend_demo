from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, AuthenticationFailed
from rest_framework.request import Request
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.whouse_manager.models import WhouseManager
from apps.whouse_manager.serializers.auth import LoginSerializer, ProfileSerializer, LogoutSerializer
from apps.whouse_manager.auth.authentication import WhouseManagerJWTAuthentication
from rest_framework.permissions import IsAuthenticated

class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        tags=["Whouse Manager Auth"],
        operation_summary="Manager Login",
        request_body=LoginSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        manager = WhouseManager.objects.filter(phone_number=data["phone_number"]).first()
        if manager is None:
            raise NotFound("Boshqaruvchi topilmadi.")

        if not manager.check_password(data["password"]):
            raise NotAuthenticated("Wrong password")

        new_session = manager.new_session()
        refresh = new_session.token
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

class ProfileAPIView(APIView):
    authentication_classes = [WhouseManagerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Whouse Manager Auth"],
        operation_summary="Manager Profile",
        responses={200: "ProfileSerializer"}
    )
    def get(self, request: HttpRequest | Request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

class LogoutAPIView(APIView):
    authentication_classes = [WhouseManagerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Whouse Manager Auth"],
        operation_summary="Manager Logout",
        request_body=LogoutSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            from apps.session.models import WhouseManagerSession
            token = RefreshToken(refresh_token)
            session_id = token.payload.get("session")
            if session_id:
                WhouseManagerSession.objects.filter(id=session_id).delete()
        except TokenError:
            return Response({"detail": "Invalid or expired token"}, status=400)
            
        return Response({"detail": "Logged out successfully."})

class CustomTokenRefreshView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        tags=["Whouse Manager Auth"],
        operation_summary="Refresh Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)}
        ),
    )
    def post(self, request, *args, **kwargs):   
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise AuthenticationFailed("Refresh token is required")

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        except TokenError as e:
            raise AuthenticationFailed(f"Invalid refresh token: {str(e)}")

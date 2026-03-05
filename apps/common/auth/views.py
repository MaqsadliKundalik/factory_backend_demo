from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, AuthenticationFailed
from rest_framework.request import Request
from data.users.models import FactoryUser
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.drivers.models import Driver
from apps.session.models import (
    DriverSession,
    FactoryUserSession
)
from .serializers import (
    UnifiedLoginSerializer, 
    DriverProfileSerializer,
    UnifiedLogoutSerializer,
    UnifiedChangePasswordSerializer,
    FactoryUserProfileSerializer
)
from .authentication import UnifiedJWTAuthentication

class UnifiedLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UnifiedLoginSerializer

    @swagger_auto_schema(
        tags=["Web Unified Auth"],
        operation_summary="Unified Web Login",
        operation_description="Login for both Whouse Managers and Factory Operators.",
        request_body=UnifiedLoginSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = UnifiedLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = None
        role = None

        # Try Manager
        user = FactoryUser.objects.filter(phone_number=data["phone_number"]).first()
        if user:
            role = user.role

        if user is None or role in ["driver", "guard"]:
            raise NotFound("Пользователь не найден.")

        if not user.check_password(data["password"]):
            raise NotAuthenticated("Неверный пароль.")

        new_session = user.new_session()
        refresh = new_session.token
        
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "role": role
        })

class UnifiedProfileAPIView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Web Unified Auth"],
        operation_summary="Get Profile",
        responses={200: FactoryUserProfileSerializer()}
    )
    def get(self, request: HttpRequest | Request):
        if isinstance(request.user, FactoryUser):
            serializer = FactoryUserProfileSerializer(request.user)
        elif isinstance(request.user, Driver):
            serializer = DriverProfileSerializer(request.user)
        else:
            raise NotFound("Foydalanuvchi topilmadi.")
        return Response(serializer.data)

class UnifiedLogoutAPIView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Web Unified Auth"],
        operation_summary="Logout",
        request_body=UnifiedLogoutSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = UnifiedLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            token = RefreshToken(refresh_token)
            session_id = token.payload.get("session")
            
            if session_id:
                FactoryUserSession.objects.filter(id=session_id).delete()
        except TokenError:
            return Response({"detail": "Токен недействителен или истёк."}, status=400)
            
        return Response({"detail": "Вы успешно вышли из системы."})

class UnifiedChangePasswordAPIView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Web Unified Auth"],
        operation_summary="Change Password",
        request_body=UnifiedChangePasswordSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = UnifiedChangePasswordSerializer(
            data=request.data,
            context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Invalidate old sessions
        FactoryUserSession.objects.filter(factory_user=user).delete()
            
        new_session = user.new_session()
        refresh = new_session.token
        
        return Response({
            "detail": "Пароль успешно изменён.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

class UnifiedTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        tags=["Web Unified Auth"],
        operation_summary="Refresh Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"refresh": openapi.Schema(type=openapi.TYPE_STRING)}
        ),
    )
    def post(self, request, *args, **kwargs):   
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise AuthenticationFailed("Требуется refresh-токен.")

        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        except TokenError as e:
            raise AuthenticationFailed(f"Недействительный refresh-токен: {str(e)}")

# --- MOBILE UNIFIED AUTH ---

class UnifiedMobileLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UnifiedLoginSerializer

    @swagger_auto_schema(
        tags=["Mobile Unified Auth"],
        operation_summary="Unified Mobile Login",
        operation_description="Login for both Drivers and Guards.",
        request_body=UnifiedLoginSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = UnifiedLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = None
        role = None

        # Try Driver
        user = Driver.objects.filter(phone_number=data["phone_number"]).first()
        if user:
            role = "driver"
        else:
            # Try Guard
            user = FactoryUser.objects.filter(phone_number=data["phone_number"], role="guard").first()
            if user:
                role = "guard"

        if user is None:
            raise NotFound("Пользователь не найден.")

        if not user.check_password(data["password"]):
            raise NotAuthenticated(f"Noto'g'ri parol. {user.check_password(data['password'])}\n{user.password}\n{data['password']}")

        new_session = user.new_session()
        refresh = new_session.token
        
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "role": role
        })

class UnifiedMobileProfileAPIView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Mobile Unified Auth"],
        operation_summary="Get Mobile Profile",
        responses={200: FactoryUserProfileSerializer()}
    )
    def get(self, request: HttpRequest | Request):
        if isinstance(request.user, Driver):
            serializer = DriverProfileSerializer(request.user)
        else:
            serializer = FactoryUserProfileSerializer(request.user)
        return Response(serializer.data)

class UnifiedMobileLogoutAPIView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Mobile Unified Auth"],
        operation_summary="Mobile Logout",
        request_body=UnifiedLogoutSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = UnifiedLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            token = RefreshToken(refresh_token)
            session_id = token.payload.get("session")
            role = token.payload.get("role")
            
            if session_id and role:
                if role == "driver":
                    DriverSession.objects.filter(id=session_id).delete()
                elif role == "guard":
                    FactoryUserSession.objects.filter(id=session_id).delete()
                    
        except TokenError:
            return Response({"detail": "Токен недействителен или истёк."}, status=400)
            
        return Response({"detail": "Вы успешно вышли из системы."})

class UnifiedMobileChangePasswordAPIView(APIView):
    authentication_classes = [UnifiedJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Mobile Unified Auth"],
        operation_summary="Mobile Change Password",
        request_body=UnifiedChangePasswordSerializer,
    )
    def post(self, request: HttpRequest | Request):
        serializer = UnifiedChangePasswordSerializer(
            data=request.data,
            context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Invalidate old sessions
        role = "driver" if isinstance(user, Driver) else "guard"
        if role == "driver":
            DriverSession.objects.filter(driver=user).delete()
        else:
            FactoryUserSession.objects.filter(factory_user=user).delete()
            
        new_session = user.new_session()
        refresh = new_session.token
        
        return Response({
            "detail": "Пароль успешно изменён.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

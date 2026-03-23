from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, AuthenticationFailed
from rest_framework.request import Request
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from data.session.models import DriverSession
from drf_yasg import openapi
from data.drivers.models import Driver
from data.drivers.auth.serializers import LoginSerializer

class CustomTokenRefreshView(APIView):
    permission_classes = []  # No authentication required for this view

    @swagger_auto_schema(
        tags=["Driver Auth"],
        operation_summary="Refresh Token",
        operation_description="Get a new access token using a refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token")
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access": openapi.Schema(type=openapi.TYPE_STRING, description="New JWT Access Token"),
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token")
                }
            ),
            401: "Invalid or expired refresh token"
        }
    )
    def post(self, request, *args, **kwargs):   
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            raise AuthenticationFailed("Refresh token is required")

        try:
            # Decode the refresh token to create a new access token

            refresh = RefreshToken(refresh_token)

            # Create a new access token using the refresh token
            access_token = refresh.access_token

            # Return the new access token
            return Response(
                {
                    "access": str(access_token),
                    "refresh": str(refresh),
                }
            )

        except TokenError as e:
            raise AuthenticationFailed(f"Invalid refresh token: {str(e)}")



class LoginAPIView(APIView):

    serializer_class = LoginSerializer

    @swagger_auto_schema(
        tags=["Driver Auth"],
        operation_summary="Driver Login",
        operation_description="Authenticate a driver using phone number and password.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Access Token"),
                    "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token")
                }
            ),
            404: "Driver not found",
            401: "Wrong password"
        }
    )
    def post(self, request: HttpRequest | Request):

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        driver = Driver.objects.filter(
            phone_number=data["phone_number"],
        ).first()

        if driver is None:
            raise NotFound("Driver topilmadi.")

        if not driver.check_password(data["password"]):

            raise NotAuthenticated("Wrong password")

        new_session = driver.new_session()

        refresh = new_session.token

        access_token = str(refresh.access_token)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
            }
        )

from .authentication import DriverJWTAuthentication
from rest_framework.permissions import IsAuthenticated

class ProfileAPIView(APIView):
    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Driver Auth"],
        operation_summary="Driver Profile",
        operation_description="Get the profile details of the currently authenticated driver.",
        responses={
            200: "ProfileSerializer",  # Replaced dynamically inside method if possible, but we'll use string here as reference, ideally we import it, so let's import it here or at top
            401: "Unauthorized"
        }
    )
    def get(self, request: HttpRequest | Request):
        from .serializers import ProfileSerializer
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

class LogoutAPIView(APIView):
    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Driver Auth"],
        operation_summary="Driver Logout",
        operation_description="Logout the driver by deleting their session and blacklisting the refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token")
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Success message")
                }
            ),
            400: "Invalid or expired token",
            401: "Unauthorized"
        }
    )
    def post(self, request: HttpRequest | Request):
        from .serializers import LogoutSerializer

        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]

        try:
            token = RefreshToken(refresh_token)
            session_id = token.payload.get("session")
            
            if session_id:
                DriverSession.objects.filter(id=session_id).delete()
                
        except TokenError:
            return Response({"detail": "Токен недействителен или истёк."}, status=400)
            
        return Response({"detail": "Вы успешно вышли из системы."})

class ChangePasswordAPIView(APIView):
    authentication_classes = [DriverJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Driver Auth"],
        operation_summary="Change Password",
        operation_description="Change the authenticated driver's password. Expects old_password and new_password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "old_password": openapi.Schema(type=openapi.TYPE_STRING, description="Current password"),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING, description="New password (min 8 chars)")
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="New JWT Access Token"),
                    "refresh_token": openapi.Schema(type=openapi.TYPE_STRING, description="New JWT Refresh Token")
                }
            ),
            400: "Validation Error (e.g., incorrect old password)",
            401: "Unauthorized"
        }
    )
    def post(self, request: HttpRequest | Request):
        from .serializers import ChangePasswordSerializer

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"driver": request.user}
        )
        serializer.is_valid(raise_exception=True)

        driver = serializer.save()
        
        # Invalidate old sessions
        DriverSession.objects.filter(driver=driver).delete()
        
        # Create new session
        new_session = driver.new_session()
        refresh = new_session.token
        
        return Response({
            "detail": "Пароль успешно изменён.",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

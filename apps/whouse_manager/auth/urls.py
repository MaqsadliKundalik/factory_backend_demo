from django.urls import path
from .views import LoginAPIView, ProfileAPIView, LogoutAPIView, CustomTokenRefreshView
from .reset_password import ChangePasswordAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("me/", ProfileAPIView.as_view(), name="profile"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
]

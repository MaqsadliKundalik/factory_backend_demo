from django.urls import path
from .views import LoginAPIView, CustomTokenRefreshView, ProfileAPIView, LogoutAPIView, ChangePasswordAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ProfileAPIView.as_view(), name="profile"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
]

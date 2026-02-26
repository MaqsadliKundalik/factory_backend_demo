from django.urls import path
from .views import (
    UnifiedLoginAPIView,
    UnifiedProfileAPIView,
    UnifiedLogoutAPIView,
    UnifiedChangePasswordAPIView,
    UnifiedTokenRefreshView
)

urlpatterns = [
    path("login/", UnifiedLoginAPIView.as_view(), name="login"),
    path("me/", UnifiedProfileAPIView.as_view(), name="profile"),
    path("logout/", UnifiedLogoutAPIView.as_view(), name="logout"),
    path("change-password/", UnifiedChangePasswordAPIView.as_view(), name="change_password"),
    path("refresh/", UnifiedTokenRefreshView.as_view(), name="token_refresh"),
]

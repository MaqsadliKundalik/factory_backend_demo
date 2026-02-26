from django.urls import path
from .views import (
    UnifiedLoginAPIView,
    UnifiedProfileAPIView,
    UnifiedLogoutAPIView,
    UnifiedChangePasswordAPIView,
    UnifiedTokenRefreshView,
    # Mobile
    UnifiedMobileLoginAPIView,
    UnifiedMobileProfileAPIView,
    UnifiedMobileLogoutAPIView,
    UnifiedMobileChangePasswordAPIView
)

urlpatterns = [
    # Web Platform
    path("web/login/", UnifiedLoginAPIView.as_view(), name="web_login"),
    path("web/me/", UnifiedProfileAPIView.as_view(), name="web_profile"),
    path("web/logout/", UnifiedLogoutAPIView.as_view(), name="web_logout"),
    path("web/change-password/", UnifiedChangePasswordAPIView.as_view(), name="web_change_password"),
    
    # Mobile Platform
    path("mobile/login/", UnifiedMobileLoginAPIView.as_view(), name="mobile_login"),
    path("mobile/me/", UnifiedMobileProfileAPIView.as_view(), name="mobile_profile"),
    path("mobile/logout/", UnifiedMobileLogoutAPIView.as_view(), name="mobile_logout"),
    path("mobile/change-password/", UnifiedMobileChangePasswordAPIView.as_view(), name="mobile_change_password"),

    # Common
    path("refresh/", UnifiedTokenRefreshView.as_view(), name="token_refresh"),
]

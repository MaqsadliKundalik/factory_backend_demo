"""
URL configuration for factory project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.drivers.urls import urlpatterns as driver_urls
from data.whouse.urls import urlpatterns as whouse_urls
from apps.common.auth.urls import urlpatterns as auth_urls
from apps.whouse_manager.urls import urlpatterns as whouse_manager_urls
from apps.factory_operator.urls import urlpatterns as factory_operator_urls
from apps.guard.urls import urlpatterns as guard_urls
from data.products.urls import urlpatterns as products_urls
from data.transports.urls import urlpatterns as transports_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Factory Management API",
        default_version='v1',
        description="Unified API for Factory Management System",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('auth/', include(auth_urls)),
    path('common/', include('apps.common.urls')),

    path('whouse-managers/', include(whouse_manager_urls)),
    path('factory-operators/', include(factory_operator_urls)),
    path('whouse/', include(whouse_urls)),

    path('drivers/', include(driver_urls)),
    path('guards/', include(guard_urls)),
    path('products/', include(products_urls)),
    path('transports/', include(transports_urls)),

    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

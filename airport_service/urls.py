"""
URL configuration for airport_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/airport/", include("flights.urls", namespace="airport")),
    path("api/v1/user/", include("user.urls", namespace="user")),

    path('api/v1/schema/', SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/doc/swagger/", SpectacularSwaggerView.as_view(
        url_name="schema"), name="swagger-ui"),
    path("api/v1/doc/redoc/", SpectacularRedocView.as_view(
        url_name="schema"), name="redoc"),

    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

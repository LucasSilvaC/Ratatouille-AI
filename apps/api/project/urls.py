"""Mapa principal de URLs. O app api recebe os caminhos que começam com /api/."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('api/', include('apps.urls')),
]

if not settings.PUBLIC_DEPLOYMENT:
    urlpatterns.append(path('admin/', admin.site.urls))

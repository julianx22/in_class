from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include(("core.urls","core"), namespace="core")),
    path("admin/", admin.site.urls),
]

# config/urls.py

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Servir archivos de MEDIA en desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

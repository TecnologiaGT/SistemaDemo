from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("clientes/", include("clientes.urls")),
    path("proveedores/", include("proveedores.urls")),
    path("productos/", include("productos.urls")),
    path("inventario/", include("inventario.urls")),
    path("ventas/", include("ventas.urls")),
    path("compras/", include("compras.urls")),
    path("reportes/", include("reportes.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

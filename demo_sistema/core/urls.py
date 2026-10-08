from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from . import pwa

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("manifest.webmanifest", pwa.manifest_view, name="manifest"),
    path("sw.js", pwa.service_worker_view, name="service_worker"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("tiendas/", views.TiendaListView.as_view(), name="tienda_list"),
    path("tiendas/nueva/", views.TiendaCreateView.as_view(), name="tienda_create"),
    path("tiendas/<int:pk>/editar/", views.TiendaUpdateView.as_view(), name="tienda_update"),
    path("tiendas/<int:pk>/toggle/", views.TiendaToggleView.as_view(), name="tienda_toggle"),

    path("empleados/", views.EmpleadoListView.as_view(), name="empleado_list"),
    path("empleados/nuevo/", views.EmpleadoCreateView.as_view(), name="empleado_create"),
    path("empleados/<int:pk>/editar/", views.EmpleadoUpdateView.as_view(), name="empleado_update"),
    path("empleados/<int:pk>/toggle/", views.EmpleadoToggleView.as_view(), name="empleado_toggle"),

    path("personalizacion/", views.PersonalizacionView.as_view(), name="personalizacion"),
    path("personalizacion/foto/", views.PersonalizacionFotoView.as_view(), name="personalizacion_foto"),

    path("reiniciar-sistema/", views.ReiniciarSistemaView.as_view(), name="reiniciar_sistema"),
]

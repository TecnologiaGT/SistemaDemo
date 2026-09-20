from django.urls import path
from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.ClienteListView.as_view(), name="list"),
    path("exportar/", views.ClienteExportarView.as_view(), name="exportar"),
    path("nuevo/", views.ClienteFormView.as_view(), name="create"),
    path("<int:pk>/editar/", views.ClienteFormView.as_view(), name="update"),
    path("<int:pk>/toggle/", views.ClienteToggleView.as_view(), name="toggle"),
    path("buscar/", views.buscar_clientes, name="buscar"),
]

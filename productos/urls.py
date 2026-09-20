from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    path("", views.ProductoListView.as_view(), name="list"),
    path("exportar/", views.ProductoExportarView.as_view(), name="exportar"),
    path("nuevo/", views.ProductoCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="update"),
    path("<int:pk>/toggle/", views.ProductoToggleView.as_view(), name="toggle"),
    path("buscar/", views.buscar_productos, name="buscar"),
]

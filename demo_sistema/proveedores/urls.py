from django.urls import path
from . import views

app_name = "proveedores"

urlpatterns = [
    path("", views.ProveedorListView.as_view(), name="list"),
    path("nuevo/", views.ProveedorFormView.as_view(), name="create"),
    path("<int:pk>/editar/", views.ProveedorFormView.as_view(), name="update"),
    path("<int:pk>/toggle/", views.ProveedorToggleView.as_view(), name="toggle"),
    path("buscar/", views.buscar_proveedores, name="buscar"),
]

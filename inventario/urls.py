from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.InventarioListView.as_view(), name="list"),
    path("exportar/", views.InventarioExportarView.as_view(), name="exportar"),
    path("traspasos/", views.TraspasoListView.as_view(), name="traspaso_list"),
    path("traspasos/nuevo/", views.TraspasoCreateView.as_view(), name="traspaso_create"),
    path("traspasos/<int:pk>/anular/", views.TraspasoAnularView.as_view(), name="traspaso_anular"),
]

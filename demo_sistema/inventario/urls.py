from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.InventarioListView.as_view(), name="list"),
    path("exportar/", views.InventarioExportarView.as_view(), name="exportar"),
    path("lotes/", views.LoteListView.as_view(), name="lote_list"),
    path("lotes/nuevo/", views.LoteCreateView.as_view(), name="lote_create"),
    path("lotes/<int:pk>/eliminar/", views.LoteEliminarView.as_view(), name="lote_eliminar"),
    path("traspasos/", views.TraspasoListView.as_view(), name="traspaso_list"),
    path("traspasos/nuevo/", views.TraspasoCreateView.as_view(), name="traspaso_create"),
    path("traspasos/<int:pk>/anular/", views.TraspasoAnularView.as_view(), name="traspaso_anular"),
]

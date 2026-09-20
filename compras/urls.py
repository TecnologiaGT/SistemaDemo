from django.urls import path
from . import views

app_name = "compras"

urlpatterns = [
    path("nueva/", views.CompraCreateView.as_view(), name="create"),
    path("cuentas-por-pagar/", views.CuentasPorPagarListView.as_view(), name="cuentas_por_pagar"),
    path("", views.CompraListView.as_view(), name="list"),
    path("exportar/", views.CompraExportarView.as_view(), name="exportar"),
    path("<int:pk>/", views.CompraDetailView.as_view(), name="detalle"),
    path("<int:pk>/anular/", views.CompraAnularView.as_view(), name="anular"),
    path("<int:pk>/abono/", views.AbonoCompraCreateView.as_view(), name="abono"),
]

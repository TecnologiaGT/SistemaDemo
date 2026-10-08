from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("caja/", views.CajaView.as_view(), name="caja"),
    path("cuentas-por-cobrar/", views.CuentasPorCobrarListView.as_view(), name="cuentas_por_cobrar"),
    path("cierres/", views.CierreCajaListView.as_view(), name="cierre_list"),
    path("cierres/nuevo/", views.CierreCajaCreateView.as_view(), name="cierre_create"),
    path("cotizaciones/", views.CotizacionListView.as_view(), name="cotizacion_list"),
    path("cotizaciones/nueva/", views.CotizacionCreateView.as_view(), name="cotizacion_create"),
    path("cotizaciones/<int:pk>/", views.CotizacionDetailView.as_view(), name="cotizacion_detalle"),
    path("cotizaciones/<int:pk>/convertir/", views.CotizacionConvertirView.as_view(), name="cotizacion_convertir"),
    path("cotizaciones/<int:pk>/anular/", views.CotizacionAnularView.as_view(), name="cotizacion_anular"),
    path("", views.VentaListView.as_view(), name="list"),
    path("exportar/", views.VentaExportarView.as_view(), name="exportar"),
    path("<int:pk>/", views.VentaDetailView.as_view(), name="detalle"),
    path("<int:pk>/ticket/", views.VentaTicketView.as_view(), name="ticket"),
    path("<int:pk>/anular/", views.VentaAnularView.as_view(), name="anular"),
    path("<int:pk>/abono/", views.AbonoVentaCreateView.as_view(), name="abono"),
    path("devolucion/", views.DevolucionView.as_view(), name="devolucion"),
]

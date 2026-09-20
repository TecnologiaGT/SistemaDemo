from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("caja/", views.CajaView.as_view(), name="caja"),
    path("", views.VentaListView.as_view(), name="list"),
    path("exportar/", views.VentaExportarView.as_view(), name="exportar"),
    path("<int:pk>/", views.VentaDetailView.as_view(), name="detalle"),
    path("<int:pk>/ticket/", views.VentaTicketView.as_view(), name="ticket"),
    path("<int:pk>/anular/", views.VentaAnularView.as_view(), name="anular"),
    path("devolucion/", views.DevolucionView.as_view(), name="devolucion"),
]

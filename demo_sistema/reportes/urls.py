from django.urls import path
from . import views

app_name = "reportes"

urlpatterns = [
    path("", views.ReportesMenuView.as_view(), name="menu"),
    path("ventas-por-tienda/", views.VentasPorTiendaView.as_view(), name="ventas_tienda"),
    path("ventas-por-empleado/", views.VentasPorEmpleadoView.as_view(), name="ventas_empleado"),
]

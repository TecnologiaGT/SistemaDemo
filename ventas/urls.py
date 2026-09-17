from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("caja/", views.CajaView.as_view(), name="caja"),
    path("", views.VentaListView.as_view(), name="list"),
    path("<int:pk>/", views.VentaDetailView.as_view(), name="detalle"),
    path("<int:pk>/anular/", views.VentaAnularView.as_view(), name="anular"),
    path("devolucion/", views.DevolucionView.as_view(), name="devolucion"),
]

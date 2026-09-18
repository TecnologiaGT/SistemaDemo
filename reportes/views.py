from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.shortcuts import render
from django.views import View

from core.permissions import AdminRequiredMixin
from ventas.models import Venta
from .utils import parsear_fecha, rango_mes_actual


class ReportesMenuView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = "reportes/menu.html"

    def get(self, request):
        return render(request, self.template_name)


def _rango_desde_request(request):
    primer_dia, ultimo_dia = rango_mes_actual()
    fecha_inicio = parsear_fecha(request.GET.get("fecha_inicio"), primer_dia)
    fecha_fin = parsear_fecha(request.GET.get("fecha_fin"), ultimo_dia)
    return fecha_inicio, fecha_fin


class VentasPorTiendaView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = "reportes/ventas_por_tienda.html"

    def get(self, request):
        fecha_inicio, fecha_fin = _rango_desde_request(request)

        ventas = Venta.objects.filter(
            tipo="V", estado="V",
            fecha__date__gte=fecha_inicio, fecha__date__lte=fecha_fin,
        )
        filas = (
            ventas.values("tienda__id", "tienda__nombre")
            .annotate(num_ventas=Count("numero"), total=Sum("total"))
            .order_by("tienda__nombre")
        )
        total_general = ventas.aggregate(total=Sum("total"))["total"] or 0
        num_ventas_total = ventas.count()

        return render(request, self.template_name, {
            "filas": filas,
            "total_general": total_general,
            "num_ventas_total": num_ventas_total,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        })


class VentasPorEmpleadoView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = "reportes/ventas_por_empleado.html"

    def get(self, request):
        fecha_inicio, fecha_fin = _rango_desde_request(request)

        ventas = Venta.objects.filter(
            tipo="V", estado="V",
            fecha__date__gte=fecha_inicio, fecha__date__lte=fecha_fin,
        )
        filas = (
            ventas.values("empleado__id", "empleado__nombre")
            .annotate(num_ventas=Count("numero"), total=Sum("total"))
            .order_by("empleado__nombre")
        )
        total_general = ventas.aggregate(total=Sum("total"))["total"] or 0
        num_ventas_total = ventas.count()

        return render(request, self.template_name, {
            "filas": filas,
            "total_general": total_general,
            "num_ventas_total": num_ventas_total,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        })

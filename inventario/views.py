from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from core.models import Tienda, Empleado
from productos.models import Producto
from .models import Inventario, Traspaso, TraspasoDetalle


def _empleado_actual(request):
    return Empleado.objects.filter(usuario=request.user).first()


def _ajustar_inventario(tienda, producto, delta):
    inv, _ = Inventario.objects.get_or_create(tienda=tienda, producto=producto)
    inv.existencia = max(0, inv.existencia + delta)
    inv.save(update_fields=["existencia"])


class InventarioListView(LoginRequiredMixin, View):
    template_name = "inventario/list.html"

    def get(self, request):
        tienda_id = request.GET.get("tienda")
        tiendas = Tienda.objects.all()
        if tienda_id:
            filas = Inventario.objects.filter(tienda_id=tienda_id).select_related("producto", "tienda").order_by("producto__nombre")
            modo = "tienda"
        else:
            filas = (
                Inventario.objects.values("producto__id", "producto__nombre", "producto__codigo")
                .annotate(existencia_total=Sum("existencia"))
                .order_by("producto__nombre")
            )
            modo = "general"
        return render(request, self.template_name, {
            "tiendas": tiendas, "filas": filas, "modo": modo, "tienda_id": tienda_id,
        })


class TraspasoListView(LoginRequiredMixin, ListView):
    model = Traspaso
    template_name = "inventario/traspaso_list.html"
    context_object_name = "traspasos"
    paginate_by = 50


class TraspasoCreateView(LoginRequiredMixin, View):
    template_name = "inventario/traspaso_form.html"

    def get(self, request):
        return render(request, self.template_name, {
            "tiendas": Tienda.objects.filter(activa=True),
            "productos": Producto.objects.filter(activo=True),
            "empleados": Empleado.objects.filter(activo=True),
            "empleado_actual": _empleado_actual(request),
        })

    def post(self, request):
        origen_id = request.POST.get("tienda_origen")
        destino_id = request.POST.get("tienda_destino")
        empleado_id = request.POST.get("empleado") or None
        comentario = request.POST.get("comentario", "")
        producto_ids = request.POST.getlist("producto_id[]")
        cantidades = request.POST.getlist("cantidad[]")

        if not origen_id or not destino_id:
            messages.error(request, "Selecciona tienda de origen y destino.")
            return redirect("inventario:traspaso_create")
        if origen_id == destino_id:
            messages.error(request, "La tienda de origen y destino no pueden ser la misma.")
            return redirect("inventario:traspaso_create")
        if not producto_ids:
            messages.error(request, "Agrega al menos un producto al traspaso.")
            return redirect("inventario:traspaso_create")

        origen = get_object_or_404(Tienda, pk=origen_id)
        destino = get_object_or_404(Tienda, pk=destino_id)
        empleado = Empleado.objects.filter(pk=empleado_id).first() if empleado_id else _empleado_actual(request)

        traspaso = Traspaso.objects.create(
            tienda_origen=origen, tienda_destino=destino, empleado=empleado, comentario=comentario, estado="V"
        )
        for pid, cant in zip(producto_ids, cantidades):
            producto = Producto.objects.filter(pk=pid).first()
            if not producto:
                continue
            cantidad = int(cant)
            TraspasoDetalle.objects.create(traspaso=traspaso, producto=producto, cantidad=cantidad)
            _ajustar_inventario(origen, producto, -cantidad)
            _ajustar_inventario(destino, producto, cantidad)

        messages.success(request, f"Traspaso #{traspaso.numero} registrado correctamente.")
        return redirect("inventario:traspaso_list")


class TraspasoAnularView(LoginRequiredMixin, View):
    def post(self, request, pk):
        traspaso = get_object_or_404(Traspaso, pk=pk)
        if traspaso.estado == "A":
            messages.warning(request, "Este traspaso ya estaba anulado.")
            return redirect("inventario:traspaso_list")
        for d in traspaso.detalle.all():
            _ajustar_inventario(traspaso.tienda_origen, d.producto, d.cantidad)
            _ajustar_inventario(traspaso.tienda_destino, d.producto, -d.cantidad)
        traspaso.estado = "A"
        traspaso.save(update_fields=["estado"])
        messages.success(request, f"Traspaso #{traspaso.numero} anulado.")
        return redirect("inventario:traspaso_list")

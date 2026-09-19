from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from core.models import Tienda, Empleado
from proveedores.models import Proveedor
from productos.models import Producto
from inventario.models import Inventario
from .models import Compra, CompraDetalle


def _empleado_actual(request):
    return Empleado.objects.filter(usuario=request.user).first()


def _ajustar_inventario(tienda, producto, delta):
    inv, _ = Inventario.objects.get_or_create(tienda=tienda, producto=producto)
    inv.existencia = max(0, inv.existencia + delta)
    inv.save(update_fields=["existencia"])


class CompraCreateView(LoginRequiredMixin, View):
    template_name = "compras/form.html"

    def get(self, request):
        return render(request, self.template_name, {
            "tiendas": Tienda.objects.filter(activa=True),
            "proveedores": Proveedor.objects.filter(activo=True),
            "productos": Producto.objects.filter(activo=True),
            "empleados": Empleado.objects.filter(activo=True),
            "empleado_actual": _empleado_actual(request),
        })

    def post(self, request):
        tienda_id = request.POST.get("tienda")
        proveedor_id = request.POST.get("proveedor")
        empleado_id = request.POST.get("empleado") or None
        producto_ids = request.POST.getlist("producto_id[]")
        cantidades = request.POST.getlist("cantidad[]")
        precios = request.POST.getlist("precio_unitario[]")

        tienda = get_object_or_404(Tienda, pk=tienda_id) if tienda_id else None
        proveedor = get_object_or_404(Proveedor, pk=proveedor_id) if proveedor_id else None
        if not tienda or not proveedor:
            messages.error(request, "Debes seleccionar tienda y proveedor.")
            return redirect("compras:create")
        if not producto_ids:
            messages.error(request, "Agrega al menos un producto a la compra.")
            return redirect("compras:create")

        empleado = Empleado.objects.filter(pk=empleado_id).first() if empleado_id else _empleado_actual(request)

        compra = Compra.objects.create(estado="V", tienda=tienda, proveedor=proveedor, empleado=empleado)
        for pid, cant, precio in zip(producto_ids, cantidades, precios):
            producto = Producto.objects.filter(pk=pid).first()
            if not producto:
                continue
            cantidad = int(cant)
            precio_unitario = Decimal(precio)
            CompraDetalle.objects.create(
                compra=compra, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario
            )
            _ajustar_inventario(tienda, producto, cantidad)

        compra.recalcular_total()
        messages.success(request, f"Compra #{compra.numero} registrada correctamente.")
        return redirect("compras:detalle", pk=compra.numero)


class CompraListView(LoginRequiredMixin, ListView):
    model = Compra
    template_name = "compras/list.html"
    context_object_name = "compras"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("tienda", "proveedor", "empleado")
        tienda_id = self.request.GET.get("tienda")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tiendas"] = Tienda.objects.all()
        return ctx


class CompraDetailView(LoginRequiredMixin, DetailView):
    model = Compra
    template_name = "compras/detalle.html"
    context_object_name = "compra"
    pk_url_kwarg = "pk"


class CompraAnularView(LoginRequiredMixin, View):
    def post(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)
        if compra.estado == "A":
            messages.warning(request, "Esta compra ya estaba anulada.")
            return redirect("compras:list")
        comentario = request.POST.get("comentario", "")
        for d in compra.detalle.all():
            _ajustar_inventario(compra.tienda, d.producto, -d.cantidad)  # se resta lo que había sumado
        compra.estado = "A"
        compra.comentario_anulacion = comentario
        compra.save(update_fields=["estado", "comentario_anulacion"])
        messages.success(request, f"Compra #{compra.numero} anulada.")
        return redirect("compras:list")

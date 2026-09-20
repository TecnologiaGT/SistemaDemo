from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from core.models import Tienda, Empleado
from core.exportar_excel import exportar_filas_excel
from proveedores.models import Proveedor
from productos.models import Producto
from inventario.servicios import ajustar_inventario
from .models import Compra, CompraDetalle, AbonoCompra


def _empleado_actual(request):
    return Empleado.objects.filter(usuario=request.user).first()


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
        forma_pago = request.POST.get("forma_pago") or "efectivo"
        if forma_pago not in dict(Compra.FORMAS_PAGO):
            forma_pago = "efectivo"

        tienda = get_object_or_404(Tienda, pk=tienda_id) if tienda_id else None
        proveedor = get_object_or_404(Proveedor, pk=proveedor_id) if proveedor_id else None
        if not tienda or not proveedor:
            messages.error(request, "Debes seleccionar tienda y proveedor.")
            return redirect("compras:create")
        if not producto_ids:
            messages.error(request, "Agrega al menos un producto a la compra.")
            return redirect("compras:create")

        empleado = Empleado.objects.filter(pk=empleado_id).first() if empleado_id else _empleado_actual(request)

        with transaction.atomic():
            compra = Compra.objects.create(
                estado="V", tienda=tienda, proveedor=proveedor, empleado=empleado, forma_pago=forma_pago
            )
            for pid, cant, precio in zip(producto_ids, cantidades, precios):
                producto = Producto.objects.filter(pk=pid).first()
                if not producto:
                    continue
                cantidad = int(cant)
                precio_unitario = Decimal(precio)
                CompraDetalle.objects.create(
                    compra=compra, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario
                )
                ajustar_inventario(tienda, producto, cantidad)

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


class CompraExportarView(LoginRequiredMixin, View):
    def get(self, request):
        qs = Compra.objects.select_related("tienda", "proveedor", "empleado").order_by("-fecha")
        tienda_id = request.GET.get("tienda")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        encabezados = ["No.", "Fecha", "Tienda", "Usuario", "Proveedor", "Total", "Forma de pago", "Estado"]
        filas = (
            [
                c.numero,
                c.fecha.strftime("%d/%m/%Y %H:%M"),
                str(c.tienda),
                str(c.empleado) if c.empleado else "",
                str(c.proveedor),
                float(c.total),
                c.get_forma_pago_display(),
                c.get_estado_display(),
            ]
            for c in qs
        )
        return exportar_filas_excel("compras.xlsx", "Compras", encabezados, filas)


class CompraDetailView(LoginRequiredMixin, DetailView):
    model = Compra
    template_name = "compras/detalle.html"
    context_object_name = "compra"
    pk_url_kwarg = "pk"


class CuentasPorPagarListView(LoginRequiredMixin, View):
    template_name = "compras/cuentas_por_pagar.html"

    def get(self, request):
        compras = (
            Compra.objects.filter(estado="V", forma_pago="credito")
            .select_related("tienda", "proveedor")
            .prefetch_related("abonos")
            .order_by("-fecha")
        )
        filas = [c for c in compras if c.saldo_pendiente > 0]
        total_pendiente = sum((c.saldo_pendiente for c in filas), Decimal("0"))
        return render(request, self.template_name, {
            "filas": filas, "total_pendiente": total_pendiente,
        })


class AbonoCompraCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)
        try:
            monto = Decimal(request.POST.get("monto") or "0")
        except Exception:
            monto = Decimal("0")
        saldo = compra.saldo_pendiente
        if compra.forma_pago != "credito":
            messages.error(request, "Esta compra no es al crédito.")
        elif monto <= 0:
            messages.error(request, "El monto del abono debe ser mayor a cero.")
        elif monto > saldo:
            messages.error(request, f"El abono (Q {monto}) no puede ser mayor al saldo pendiente (Q {saldo}).")
        else:
            AbonoCompra.objects.create(compra=compra, monto=monto, comentario=request.POST.get("comentario", ""))
            messages.success(request, f"Abono de Q {monto} registrado en la Compra #{compra.numero}.")
        return redirect("compras:detalle", pk=compra.numero)


class CompraAnularView(LoginRequiredMixin, View):
    def post(self, request, pk):
        compra = get_object_or_404(Compra, pk=pk)
        if compra.estado == "A":
            messages.warning(request, "Esta compra ya estaba anulada.")
            return redirect("compras:list")
        comentario = request.POST.get("comentario", "")
        with transaction.atomic():
            for d in compra.detalle.all():
                ajustar_inventario(compra.tienda, d.producto, -d.cantidad)  # se resta lo que había sumado
            compra.estado = "A"
            compra.comentario_anulacion = comentario
            compra.save(update_fields=["estado", "comentario_anulacion"])
        messages.success(request, f"Compra #{compra.numero} anulada.")
        return redirect("compras:list")

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from core.models import Tienda, Empleado
from core.permissions import usuario_es_admin
from clientes.models import Cliente
from productos.models import Producto
from inventario.models import Inventario
from .models import Venta, VentaDetalle


def _empleado_actual(request):
    return Empleado.objects.filter(usuario=request.user).first()


def _ajustar_inventario(tienda, producto, delta):
    """Suma `delta` (puede ser negativo) a la existencia del producto en la tienda.
    Nunca deja la existencia por debajo de 0."""
    inv, _ = Inventario.objects.get_or_create(tienda=tienda, producto=producto)
    inv.existencia = max(0, inv.existencia + delta)
    inv.save(update_fields=["existencia"])


class CajaView(LoginRequiredMixin, View):
    template_name = "ventas/caja.html"

    def get(self, request):
        es_admin = usuario_es_admin(request.user)
        empleado_actual = _empleado_actual(request)

        if not es_admin and (not empleado_actual or not empleado_actual.tienda_id):
            messages.error(
                request,
                "Tu usuario no tiene una tienda asignada. Pide a un administrador que te asigne una en Empleados.",
            )
            return redirect("core:home")

        return render(request, self.template_name, {
            "es_admin": es_admin,
            "tiendas": Tienda.objects.filter(activa=True),
            "clientes": Cliente.objects.filter(activo=True),
            "productos": Producto.objects.filter(activo=True),
            "empleados": Empleado.objects.filter(activo=True),
            "empleado_actual": empleado_actual,
        })

    def post(self, request):
        es_admin = usuario_es_admin(request.user)
        empleado_actual = _empleado_actual(request)
        cliente_id = request.POST.get("cliente") or None
        producto_ids = request.POST.getlist("producto_id[]")
        cantidades = request.POST.getlist("cantidad[]")
        precios = request.POST.getlist("precio_unitario[]")

        if es_admin:
            # Un administrador puede vender a nombre de otra tienda/vendedor.
            tienda_id = request.POST.get("tienda")
            empleado_id = request.POST.get("empleado") or None
            tienda = get_object_or_404(Tienda, pk=tienda_id) if tienda_id else None
            empleado = Empleado.objects.filter(pk=empleado_id).first() if empleado_id else empleado_actual
        else:
            # Un empleado normal siempre vende con su propia tienda y como sí mismo,
            # sin importar qué se haya enviado en el formulario.
            if not empleado_actual or not empleado_actual.tienda_id:
                messages.error(
                    request,
                    "Tu usuario no tiene una tienda asignada. Pide a un administrador que te asigne una en Empleados.",
                )
                return redirect("core:home")
            tienda = empleado_actual.tienda
            empleado = empleado_actual

        if not tienda:
            messages.error(request, "Debes seleccionar una tienda.")
            return redirect("ventas:caja")
        if not producto_ids:
            messages.error(request, "Agrega al menos un producto a la venta.")
            return redirect("ventas:caja")

        cliente = Cliente.objects.filter(pk=cliente_id).first() if cliente_id else None

        venta = Venta.objects.create(tipo="V", estado="V", tienda=tienda, empleado=empleado, cliente=cliente)
        for pid, cant, precio in zip(producto_ids, cantidades, precios):
            producto = Producto.objects.filter(pk=pid).first()
            if not producto:
                continue
            cantidad = int(cant)
            precio_unitario = Decimal(precio)
            VentaDetalle.objects.create(
                venta=venta, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario
            )
            _ajustar_inventario(tienda, producto, -cantidad)

        venta.recalcular_total()
        messages.success(request, f"Venta #{venta.numero} registrada correctamente.")
        return redirect("ventas:detalle", pk=venta.numero)


class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = "ventas/list.html"
    context_object_name = "ventas"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("tienda", "cliente", "empleado")
        tienda_id = self.request.GET.get("tienda")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tiendas"] = Tienda.objects.all()
        return ctx


class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = "ventas/detalle.html"
    context_object_name = "venta"
    pk_url_kwarg = "pk"


class VentaAnularView(LoginRequiredMixin, View):
    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        if venta.estado == "A":
            messages.warning(request, "Esta venta ya estaba anulada.")
            return redirect("ventas:list")
        comentario = request.POST.get("comentario", "")
        for d in venta.detalle.all():
            _ajustar_inventario(venta.tienda, d.producto, d.cantidad)  # se regresa al inventario
        venta.estado = "A"
        venta.comentario_anulacion = comentario
        venta.save(update_fields=["estado", "comentario_anulacion"])
        messages.success(request, f"Venta #{venta.numero} anulada.")
        return redirect("ventas:list")


class DevolucionView(LoginRequiredMixin, View):
    template_name = "ventas/devolucion.html"

    def get(self, request):
        numero = request.GET.get("numero")
        venta_original = None
        if numero:
            venta_original = Venta.objects.filter(pk=numero, tipo="V").first()
            if not venta_original:
                messages.error(request, f"No se encontró la venta #{numero}.")
        return render(request, self.template_name, {"venta_original": venta_original})

    def post(self, request):
        numero = request.POST.get("numero")
        venta_original = get_object_or_404(Venta, pk=numero, tipo="V")
        if venta_original.estado == "A":
            messages.error(request, "No se puede hacer una devolución de una venta anulada.")
            return redirect("ventas:devolucion")

        devolucion = Venta.objects.create(
            tipo="D", estado="V",
            tienda=venta_original.tienda, empleado=_empleado_actual(request),
            cliente=venta_original.cliente, venta_original=venta_original,
        )
        for d in venta_original.detalle.all():
            VentaDetalle.objects.create(
                venta=devolucion, producto=d.producto,
                cantidad=d.cantidad, precio_unitario=d.precio_unitario,
            )
            _ajustar_inventario(venta_original.tienda, d.producto, d.cantidad)  # regresa al inventario

        devolucion.recalcular_total()
        messages.success(request, f"Devolución registrada para la venta #{venta_original.numero}.")
        return redirect("ventas:detalle", pk=devolucion.numero)

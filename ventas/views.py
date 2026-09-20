from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from core.models import Tienda, Empleado
from core.permissions import usuario_es_admin
from core.exportar_excel import exportar_filas_excel
from clientes.models import Cliente
from productos.models import Producto
from inventario.servicios import ajustar_inventario, StockInsuficiente
from .models import Venta, VentaDetalle, AbonoVenta, CierreCaja, Cotizacion, CotizacionDetalle


def _empleado_actual(request):
    return Empleado.objects.filter(usuario=request.user).first()


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
        try:
            descuento = Decimal(request.POST.get("descuento") or "0")
        except Exception:
            descuento = Decimal("0")
        if descuento < 0:
            descuento = Decimal("0")
        forma_pago = request.POST.get("forma_pago") or "efectivo"
        if forma_pago not in dict(Venta.FORMAS_PAGO):
            forma_pago = "efectivo"

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

        try:
            with transaction.atomic():
                venta = Venta.objects.create(
                    tipo="V", estado="V", tienda=tienda, empleado=empleado, cliente=cliente,
                    descuento=descuento, forma_pago=forma_pago,
                )
                for pid, cant, precio in zip(producto_ids, cantidades, precios):
                    producto = Producto.objects.filter(pk=pid).first()
                    if not producto:
                        continue
                    cantidad = int(cant)
                    precio_unitario = Decimal(precio)
                    VentaDetalle.objects.create(
                        venta=venta, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario
                    )
                    # validar_existencia=True: si dos cajas venden el mismo
                    # producto al mismo tiempo y ya no alcanza, esta venta
                    # completa se cancela (no se guarda nada a medias).
                    ajustar_inventario(tienda, producto, -cantidad, validar_existencia=True)
                venta.recalcular_total()
        except StockInsuficiente as error:
            messages.error(request, str(error))
            return redirect("ventas:caja")

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


class VentaExportarView(LoginRequiredMixin, View):
    def get(self, request):
        qs = Venta.objects.select_related("tienda", "cliente", "empleado").order_by("-fecha")
        tienda_id = request.GET.get("tienda")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        encabezados = [
            "No.", "Tipo", "Fecha", "Tienda", "Usuario", "Cliente",
            "Subtotal", "Descuento", "Total", "Forma de pago", "Estado",
        ]
        filas = (
            [
                v.numero,
                v.get_tipo_display(),
                v.fecha.strftime("%d/%m/%Y %H:%M"),
                str(v.tienda),
                str(v.empleado) if v.empleado else "",
                str(v.cliente) if v.cliente else "Consumidor Final",
                float(v.subtotal),
                float(v.descuento),
                float(v.total),
                v.get_forma_pago_display(),
                v.get_estado_display(),
            ]
            for v in qs
        )
        return exportar_filas_excel("ventas.xlsx", "Ventas", encabezados, filas)


class VentaDetailView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = "ventas/detalle.html"
    context_object_name = "venta"
    pk_url_kwarg = "pk"


class VentaTicketView(LoginRequiredMixin, DetailView):
    model = Venta
    template_name = "ventas/ticket.html"
    context_object_name = "venta"
    pk_url_kwarg = "pk"


class VentaAnularView(LoginRequiredMixin, View):
    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        if venta.estado == "A":
            messages.warning(request, "Esta venta ya estaba anulada.")
            return redirect("ventas:list")
        comentario = request.POST.get("comentario", "")
        with transaction.atomic():
            for d in venta.detalle.all():
                ajustar_inventario(venta.tienda, d.producto, d.cantidad)  # se regresa al inventario
            venta.estado = "A"
            venta.comentario_anulacion = comentario
            venta.save(update_fields=["estado", "comentario_anulacion"])
        messages.success(request, f"Venta #{venta.numero} anulada.")
        return redirect("ventas:list")


class CuentasPorCobrarListView(LoginRequiredMixin, View):
    template_name = "ventas/cuentas_por_cobrar.html"

    def get(self, request):
        ventas = (
            Venta.objects.filter(tipo="V", estado="V", forma_pago="credito")
            .select_related("tienda", "cliente")
            .prefetch_related("abonos")
            .order_by("-fecha")
        )
        filas = [v for v in ventas if v.saldo_pendiente > 0]
        total_pendiente = sum((v.saldo_pendiente for v in filas), Decimal("0"))
        return render(request, self.template_name, {
            "filas": filas, "total_pendiente": total_pendiente,
        })


class AbonoVentaCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        venta = get_object_or_404(Venta, pk=pk)
        try:
            monto = Decimal(request.POST.get("monto") or "0")
        except Exception:
            monto = Decimal("0")
        saldo = venta.saldo_pendiente
        if venta.forma_pago != "credito":
            messages.error(request, "Esta venta no es al crédito.")
        elif monto <= 0:
            messages.error(request, "El monto del abono debe ser mayor a cero.")
        elif monto > saldo:
            messages.error(request, f"El abono (Q {monto}) no puede ser mayor al saldo pendiente (Q {saldo}).")
        else:
            AbonoVenta.objects.create(venta=venta, monto=monto, comentario=request.POST.get("comentario", ""))
            messages.success(request, f"Abono de Q {monto} registrado en la Factura #{venta.numero}.")
        return redirect("ventas:detalle", pk=venta.numero)


class CierreCajaListView(LoginRequiredMixin, ListView):
    model = CierreCaja
    template_name = "ventas/cierre_list.html"
    context_object_name = "cierres"
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset().select_related("tienda", "empleado")


class CierreCajaCreateView(LoginRequiredMixin, View):
    template_name = "ventas/cierre_form.html"

    def _tienda_disponible(self, request):
        es_admin = usuario_es_admin(request.user)
        empleado_actual = _empleado_actual(request)
        if es_admin:
            tienda_id = request.GET.get("tienda") or request.POST.get("tienda")
            return Tienda.objects.filter(pk=tienda_id).first() if tienda_id else None
        return empleado_actual.tienda if empleado_actual and empleado_actual.tienda_id else None

    def _resumen(self, tienda):
        ultimo = CierreCaja.objects.filter(tienda=tienda).order_by("-hasta").first()
        desde = ultimo.hasta if ultimo else tienda.creado
        ventas = Venta.objects.filter(tienda=tienda, tipo="V", estado="V", fecha__gt=desde)
        totales = {"efectivo": Decimal("0"), "tarjeta": Decimal("0"), "transferencia": Decimal("0"), "credito": Decimal("0")}
        for v in ventas:
            totales[v.forma_pago] = totales.get(v.forma_pago, Decimal("0")) + v.total
        return desde, ventas.count(), totales

    def get(self, request):
        es_admin = usuario_es_admin(request.user)
        tienda = self._tienda_disponible(request)
        contexto = {
            "es_admin": es_admin,
            "tiendas": Tienda.objects.filter(activa=True),
            "tienda_sel": tienda,
        }
        if tienda:
            desde, cantidad, totales = self._resumen(tienda)
            contexto.update({"desde": desde, "cantidad_ventas": cantidad, "totales": totales})
        return render(request, self.template_name, contexto)

    def post(self, request):
        tienda = self._tienda_disponible(request)
        if not tienda:
            messages.error(request, "Selecciona una tienda para hacer el cierre.")
            return redirect("ventas:cierre_create")
        desde, cantidad, totales = self._resumen(tienda)
        try:
            efectivo_contado = Decimal(request.POST.get("efectivo_contado") or "0")
        except Exception:
            efectivo_contado = Decimal("0")
        cierre = CierreCaja.objects.create(
            tienda=tienda, empleado=_empleado_actual(request), desde=desde,
            total_efectivo=totales["efectivo"], total_tarjeta=totales["tarjeta"],
            total_transferencia=totales["transferencia"], total_credito=totales["credito"],
            cantidad_ventas=cantidad, efectivo_contado=efectivo_contado,
            comentario=request.POST.get("comentario", ""),
        )
        messages.success(request, f"Cierre de caja #{cierre.numero} registrado.")
        return redirect("ventas:cierre_list")


class CotizacionCreateView(LoginRequiredMixin, View):
    template_name = "ventas/cotizacion_form.html"

    def get(self, request):
        es_admin = usuario_es_admin(request.user)
        empleado_actual = _empleado_actual(request)
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
            tienda_id = request.POST.get("tienda")
            empleado_id = request.POST.get("empleado") or None
            tienda = get_object_or_404(Tienda, pk=tienda_id) if tienda_id else None
            empleado = Empleado.objects.filter(pk=empleado_id).first() if empleado_id else empleado_actual
        else:
            tienda = empleado_actual.tienda if empleado_actual else None
            empleado = empleado_actual

        if not tienda:
            messages.error(request, "Debes seleccionar una tienda.")
            return redirect("ventas:cotizacion_create")
        if not producto_ids:
            messages.error(request, "Agrega al menos un producto a la cotización.")
            return redirect("ventas:cotizacion_create")

        cliente = Cliente.objects.filter(pk=cliente_id).first() if cliente_id else None

        with transaction.atomic():
            cotizacion = Cotizacion.objects.create(tienda=tienda, empleado=empleado, cliente=cliente, estado="A")
            for pid, cant, precio in zip(producto_ids, cantidades, precios):
                producto = Producto.objects.filter(pk=pid).first()
                if not producto:
                    continue
                CotizacionDetalle.objects.create(
                    cotizacion=cotizacion, producto=producto,
                    cantidad=int(cant), precio_unitario=Decimal(precio),
                )
            cotizacion.recalcular_total()

        messages.success(request, f"Cotización #{cotizacion.numero} registrada correctamente.")
        return redirect("ventas:cotizacion_detalle", pk=cotizacion.numero)


class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = "ventas/cotizacion_list.html"
    context_object_name = "cotizaciones"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("tienda", "cliente")
        tienda_id = self.request.GET.get("tienda")
        if tienda_id:
            qs = qs.filter(tienda_id=tienda_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tiendas"] = Tienda.objects.all()
        return ctx


class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = "ventas/cotizacion_detalle.html"
    context_object_name = "cotizacion"
    pk_url_kwarg = "pk"


class CotizacionConvertirView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cotizacion = get_object_or_404(Cotizacion, pk=pk)
        if cotizacion.estado != "A":
            messages.error(request, "Esta cotización ya no está activa.")
            return redirect("ventas:cotizacion_detalle", pk=cotizacion.numero)

        empleado_actual = _empleado_actual(request)
        try:
            with transaction.atomic():
                venta = Venta.objects.create(
                    tipo="V", estado="V", tienda=cotizacion.tienda,
                    empleado=empleado_actual or cotizacion.empleado, cliente=cotizacion.cliente,
                )
                for d in cotizacion.detalle.all():
                    VentaDetalle.objects.create(
                        venta=venta, producto=d.producto, cantidad=d.cantidad, precio_unitario=d.precio_unitario,
                    )
                    ajustar_inventario(cotizacion.tienda, d.producto, -d.cantidad, validar_existencia=True)
                venta.recalcular_total()
                cotizacion.estado = "C"
                cotizacion.venta_generada = venta
                cotizacion.save(update_fields=["estado", "venta_generada"])
        except StockInsuficiente as error:
            messages.error(request, f"No se pudo convertir: {error}")
            return redirect("ventas:cotizacion_detalle", pk=cotizacion.numero)

        messages.success(request, f"Cotización #{cotizacion.numero} convertida en Venta #{venta.numero}.")
        return redirect("ventas:detalle", pk=venta.numero)


class CotizacionAnularView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cotizacion = get_object_or_404(Cotizacion, pk=pk)
        if cotizacion.estado != "A":
            messages.warning(request, "Esta cotización ya no está activa.")
        else:
            cotizacion.estado = "X"
            cotizacion.save(update_fields=["estado"])
            messages.success(request, f"Cotización #{cotizacion.numero} cancelada.")
        return redirect("ventas:cotizacion_list")


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

        with transaction.atomic():
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
                ajustar_inventario(venta_original.tienda, d.producto, d.cantidad)  # regresa al inventario

            devolucion.recalcular_total()
        messages.success(request, f"Devolución registrada para la venta #{venta_original.numero}.")
        return redirect("ventas:detalle", pk=devolucion.numero)

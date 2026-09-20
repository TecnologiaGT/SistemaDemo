from decimal import Decimal

from django.db import models
from core.models import Tienda, Empleado
from clientes.models import Cliente
from productos.models import Producto


class Venta(models.Model):
    TIPOS = [
        ("V", "Venta"),
        ("D", "Devolución"),
    ]
    ESTADOS = [
        ("V", "Vigente"),
        ("A", "Anulada"),
    ]
    FORMAS_PAGO = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
        ("credito", "Crédito"),
    ]
    numero = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=1, choices=TIPOS, default="V")
    estado = models.CharField(max_length=1, choices=ESTADOS, default="V")
    forma_pago = models.CharField(max_length=20, choices=FORMAS_PAGO, default="efectivo")
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="ventas")
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventas"
    )
    venta_original = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devoluciones",
        help_text="Si es una devolución, referencia a la venta original.",
    )
    fecha = models.DateTimeField(auto_now_add=True)
    descuento = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Monto en quetzales que se resta del subtotal antes del total.",
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comentario_anulacion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Factura #{self.numero}"

    @property
    def subtotal(self):
        return sum((d.subtotal for d in self.detalle.all()), Decimal("0"))

    @property
    def total_abonado(self):
        return sum((a.monto for a in self.abonos.all()), Decimal("0"))

    @property
    def saldo_pendiente(self):
        """Solo aplica a ventas al crédito, vigentes. Cualquier otro caso
        (contado, anulada, devolución) no tiene saldo pendiente."""
        if self.forma_pago != "credito" or self.estado != "V" or self.tipo != "V":
            return Decimal("0")
        saldo = self.total - self.total_abonado
        return saldo if saldo > 0 else Decimal("0")

    def recalcular_total(self):
        total = self.subtotal - self.descuento
        if total < 0:
            total = Decimal("0")
        self.total = total
        self.save(update_fields=["total"])


class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalle")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalle de ventas"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


class AbonoVenta(models.Model):
    """Pago parcial o total registrado contra una venta al crédito
    (cuentas por cobrar)."""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="abonos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Abono de venta"
        verbose_name_plural = "Abonos de venta"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Abono Q{self.monto} a Factura #{self.venta_id}"


class CierreCaja(models.Model):
    """Arqueo de caja: resume las ventas por forma de pago de una tienda
    desde el último cierre (o desde el inicio, si es el primero), y compara
    el efectivo esperado contra el efectivo que el usuario contó a mano."""
    numero = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="cierres_caja")
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    desde = models.DateTimeField()
    hasta = models.DateTimeField(auto_now_add=True)
    total_efectivo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tarjeta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transferencia = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_credito = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cantidad_ventas = models.PositiveIntegerField(default=0)
    efectivo_contado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comentario = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Cierre de caja"
        verbose_name_plural = "Cierres de caja"
        ordering = ["-hasta"]

    def __str__(self):
        return f"Cierre #{self.numero} - {self.tienda}"

    @property
    def total_general(self):
        return self.total_efectivo + self.total_tarjeta + self.total_transferencia + self.total_credito

    @property
    def diferencia(self):
        """Positivo: sobra efectivo. Negativo: falta efectivo."""
        return self.efectivo_contado - self.total_efectivo


class Cotizacion(models.Model):
    ESTADOS = [
        ("A", "Activa"),
        ("C", "Convertida a venta"),
        ("X", "Cancelada"),
    ]
    numero = models.AutoField(primary_key=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="cotizaciones")
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="cotizaciones"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default="A")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    venta_generada = models.ForeignKey(
        Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name="cotizacion_origen"
    )

    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Cotización #{self.numero}"

    def recalcular_total(self):
        total = sum((d.subtotal for d in self.detalle.all()), Decimal("0"))
        self.total = total
        self.save(update_fields=["total"])


class CotizacionDetalle(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name="detalle")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de cotización"
        verbose_name_plural = "Detalle de cotizaciones"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

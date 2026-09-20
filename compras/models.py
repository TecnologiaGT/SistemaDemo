from decimal import Decimal

from django.db import models
from core.models import Tienda, Empleado
from proveedores.models import Proveedor
from productos.models import Producto


class Compra(models.Model):
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
    estado = models.CharField(max_length=1, choices=ESTADOS, default="V")
    forma_pago = models.CharField(max_length=20, choices=FORMAS_PAGO, default="efectivo")
    tienda = models.ForeignKey(Tienda, on_delete=models.PROTECT, related_name="compras")
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="compras")
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comentario_anulacion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Compra #{self.numero}"

    @property
    def total_abonado(self):
        return sum((a.monto for a in self.abonos.all()), Decimal("0"))

    @property
    def saldo_pendiente(self):
        """Solo aplica a compras al crédito, vigentes."""
        if self.forma_pago != "credito" or self.estado != "V":
            return Decimal("0")
        saldo = self.total - self.total_abonado
        return saldo if saldo > 0 else Decimal("0")

    def recalcular_total(self):
        total = sum(d.subtotal for d in self.detalle.all())
        self.total = total
        self.save(update_fields=["total"])


class CompraDetalle(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalle")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalle de compras"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


class AbonoCompra(models.Model):
    """Pago parcial o total registrado contra una compra al crédito
    (cuentas por pagar a proveedores)."""
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="abonos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Abono de compra"
        verbose_name_plural = "Abonos de compra"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Abono Q{self.monto} a Compra #{self.compra_id}"

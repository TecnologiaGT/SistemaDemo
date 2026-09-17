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
    numero = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=1, choices=TIPOS, default="V")
    estado = models.CharField(max_length=1, choices=ESTADOS, default="V")
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
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comentario_anulacion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Factura #{self.numero}"

    def recalcular_total(self):
        total = sum(d.subtotal for d in self.detalle.all())
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

from django.db import models
from core.models import Tienda, Empleado
from proveedores.models import Proveedor
from productos.models import Producto


class Compra(models.Model):
    ESTADOS = [
        ("V", "Vigente"),
        ("A", "Anulada"),
    ]
    numero = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default="V")
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

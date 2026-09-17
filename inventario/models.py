from django.db import models
from core.models import Tienda, Empleado
from productos.models import Producto


class Inventario(models.Model):
    """Existencia de un producto en una tienda específica."""
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name="inventarios")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="inventarios")
    existencia = models.IntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventario"
        unique_together = ("tienda", "producto")
        ordering = ["tienda", "producto"]

    def __str__(self):
        return f"{self.producto.nombre} @ {self.tienda.nombre}: {self.existencia}"


class Traspaso(models.Model):
    ESTADOS = [
        ("V", "Vigente"),
        ("A", "Anulado"),
    ]
    numero = models.AutoField(primary_key=True)
    tienda_origen = models.ForeignKey(
        Tienda, on_delete=models.PROTECT, related_name="traspasos_enviados"
    )
    tienda_destino = models.ForeignKey(
        Tienda, on_delete=models.PROTECT, related_name="traspasos_recibidos"
    )
    empleado = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default="V")
    comentario = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Traspaso"
        verbose_name_plural = "Traspasos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Traspaso #{self.numero} ({self.tienda_origen} → {self.tienda_destino})"


class TraspasoDetalle(models.Model):
    traspaso = models.ForeignKey(Traspaso, on_delete=models.CASCADE, related_name="detalle")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Detalle de traspaso"
        verbose_name_plural = "Detalle de traspasos"

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

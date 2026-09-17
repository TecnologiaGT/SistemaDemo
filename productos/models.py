from django.db import models


class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    foto_principal = models.ImageField(upload_to="productos/", blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ProductoFoto(models.Model):
    """Fotos adicionales de un producto (además de la foto principal)."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="productos/galeria/")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto de producto"
        verbose_name_plural = "Fotos de producto"

    def __str__(self):
        return f"Foto de {self.producto.nombre}"

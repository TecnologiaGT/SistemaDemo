from django.db import models


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    nit_documento = models.CharField("NIT / Documento", max_length=50, blank=True)
    email = models.EmailField(blank=True)
    contacto = models.CharField(max_length=150, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ProveedorDireccion(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="direcciones")
    direccion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=150, blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Dirección de proveedor"
        verbose_name_plural = "Direcciones de proveedor"

    def __str__(self):
        return self.direccion


class ProveedorTelefono(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name="telefonos")
    telefono = models.CharField(max_length=50)
    etiqueta = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Teléfono de proveedor"
        verbose_name_plural = "Teléfonos de proveedor"

    def __str__(self):
        return self.telefono

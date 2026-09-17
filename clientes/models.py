from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    nit_documento = models.CharField("NIT / Documento", max_length=50, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ClienteDireccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="direcciones")
    direccion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=150, blank=True)
    principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Dirección de cliente"
        verbose_name_plural = "Direcciones de cliente"

    def __str__(self):
        return self.direccion


class ClienteTelefono(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="telefonos")
    telefono = models.CharField(max_length=50)
    etiqueta = models.CharField(max_length=50, blank=True, help_text="Ej: celular, casa, trabajo")

    class Meta:
        verbose_name = "Teléfono de cliente"
        verbose_name_plural = "Teléfonos de cliente"

    def __str__(self):
        return self.telefono

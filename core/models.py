from django.db import models
from django.contrib.auth.models import User


class Tienda(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    activa = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    TIPOS_USUARIO = [
        ("admin", "Administrador"),
        ("empleado", "Empleado"),
    ]

    usuario = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="empleado"
    )
    nombre = models.CharField(max_length=150)
    puesto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    tienda = models.ForeignKey(
        Tienda, on_delete=models.SET_NULL, null=True, blank=True, related_name="empleados"
    )
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO, default="empleado")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    @property
    def es_admin(self):
        return self.tipo_usuario == "admin"

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

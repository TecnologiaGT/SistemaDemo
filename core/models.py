from django.db import models
from django.contrib.auth.models import User

from .paletas import OPCIONES_PALETA, PALETA_DEFECTO


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


class Personalizacion(models.Model):
    """Configuración visual del sistema (un solo registro, pk=1).

    La foto de fondo se guarda como bytes directamente en la base de datos
    (no en el disco del servidor) para que sobreviva cada despliegue en
    Render, cuyo disco no es permanente.
    """
    paleta = models.CharField(max_length=20, choices=OPCIONES_PALETA, default=PALETA_DEFECTO)
    foto_fondo = models.BinaryField(null=True, blank=True)
    foto_fondo_tipo = models.CharField(max_length=50, blank=True)  # ej. "image/jpeg"
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personalización"
        verbose_name_plural = "Personalización"

    def __str__(self):
        return "Personalización del sistema"

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

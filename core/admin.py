from django.contrib import admin
from .models import Tienda, Empleado


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono", "activa")
    search_fields = ("nombre",)


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "puesto", "tienda", "activo")
    list_filter = ("tienda", "activo")
    search_fields = ("nombre",)

from django.contrib import admin
from .models import Proveedor, ProveedorDireccion, ProveedorTelefono


class ProveedorDireccionInline(admin.TabularInline):
    model = ProveedorDireccion
    extra = 1


class ProveedorTelefonoInline(admin.TabularInline):
    model = ProveedorTelefono
    extra = 1


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit_documento", "contacto", "activo")
    search_fields = ("nombre", "nit_documento")
    inlines = [ProveedorDireccionInline, ProveedorTelefonoInline]

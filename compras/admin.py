from django.contrib import admin
from .models import Compra, CompraDetalle


class CompraDetalleInline(admin.TabularInline):
    model = CompraDetalle
    extra = 1


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("numero", "estado", "tienda", "proveedor", "fecha", "total")
    list_filter = ("estado", "tienda")
    inlines = [CompraDetalleInline]

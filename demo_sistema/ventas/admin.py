from django.contrib import admin
from .models import Venta, VentaDetalle


class VentaDetalleInline(admin.TabularInline):
    model = VentaDetalle
    extra = 1


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "estado", "tienda", "cliente", "fecha", "total")
    list_filter = ("tipo", "estado", "tienda")
    inlines = [VentaDetalleInline]

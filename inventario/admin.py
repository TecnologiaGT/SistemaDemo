from django.contrib import admin
from .models import Inventario, Traspaso, TraspasoDetalle


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "tienda", "existencia", "actualizado")
    list_filter = ("tienda",)
    search_fields = ("producto__nombre",)


class TraspasoDetalleInline(admin.TabularInline):
    model = TraspasoDetalle
    extra = 1


@admin.register(Traspaso)
class TraspasoAdmin(admin.ModelAdmin):
    list_display = ("numero", "tienda_origen", "tienda_destino", "fecha", "estado")
    list_filter = ("estado", "tienda_origen", "tienda_destino")
    inlines = [TraspasoDetalleInline]

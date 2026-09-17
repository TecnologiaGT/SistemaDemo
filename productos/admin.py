from django.contrib import admin
from .models import Producto, ProductoFoto


class ProductoFotoInline(admin.TabularInline):
    model = ProductoFoto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "precio_compra", "precio_venta", "activo")
    search_fields = ("codigo", "nombre")
    inlines = [ProductoFotoInline]

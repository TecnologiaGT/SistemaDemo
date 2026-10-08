from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView

from core.exportar_excel import exportar_filas_excel
from .models import Producto
from .forms import ProductoForm


class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "productos/list.html"
    context_object_name = "productos"
    ordering = ["nombre"]
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/form.html"
    success_url = reverse_lazy("productos:list")

    def form_valid(self, form):
        messages.success(self.request, "Producto guardado correctamente.")
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/form.html"
    success_url = reverse_lazy("productos:list")

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


class ProductoExportarView(LoginRequiredMixin, View):
    def get(self, request):
        qs = Producto.objects.all().order_by("nombre")
        q = request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)
        encabezados = ["Código", "Nombre", "Precio compra", "Precio venta", "Stock mínimo", "Estado"]
        filas = (
            [
                p.codigo or "",
                p.nombre,
                float(p.precio_compra),
                float(p.precio_venta),
                p.stock_minimo,
                "Activo" if p.activo else "Inactivo",
            ]
            for p in qs
        )
        return exportar_filas_excel("productos.xlsx", "Productos", encabezados, filas)


class ProductoToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        producto.activo = not producto.activo
        producto.save(update_fields=["activo"])
        messages.success(request, f"Producto {'activado' if producto.activo else 'desactivado'}.")
        return redirect("productos:list")


def buscar_productos(request):
    """Buscador rápido (Shift+F12) usado en Caja y Compras.
    Si se pasa tienda_id, incluye la existencia en esa tienda."""
    from inventario.models import Inventario

    q = request.GET.get("q", "")
    tienda_id = request.GET.get("tienda_id")
    resultados = []
    if len(q) >= 1:
        productos = Producto.objects.filter(activo=True).filter(
            Q(nombre__icontains=q) | Q(codigo__icontains=q)
        )[:15]
        for p in productos:
            existencia = None
            if tienda_id:
                inv = Inventario.objects.filter(tienda_id=tienda_id, producto=p).first()
                existencia = inv.existencia if inv else 0
            resultados.append({
                "id": p.id,
                "codigo": p.codigo or "",
                "nombre": p.nombre,
                "precio_venta": str(p.precio_venta),
                "precio_compra": str(p.precio_compra),
                "existencia": existencia,
            })
    return JsonResponse({"resultados": resultados})

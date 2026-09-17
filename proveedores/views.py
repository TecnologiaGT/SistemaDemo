from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView

from .models import Proveedor
from .forms import ProveedorForm, DireccionFormSet, TelefonoFormSet


class ProveedorListView(LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = "proveedores/list.html"
    context_object_name = "proveedores"
    ordering = ["nombre"]
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs


class ProveedorFormView(LoginRequiredMixin, View):
    template_name = "proveedores/form.html"

    def get_object(self, pk):
        return get_object_or_404(Proveedor, pk=pk) if pk else None

    def get(self, request, pk=None):
        proveedor = self.get_object(pk)
        form = ProveedorForm(instance=proveedor)
        direcciones = DireccionFormSet(instance=proveedor, prefix="direcciones")
        telefonos = TelefonoFormSet(instance=proveedor, prefix="telefonos")
        return render(request, self.template_name, {
            "form": form, "direcciones": direcciones, "telefonos": telefonos, "object": proveedor,
        })

    def post(self, request, pk=None):
        proveedor = self.get_object(pk)
        form = ProveedorForm(request.POST, instance=proveedor)
        direcciones = DireccionFormSet(request.POST, instance=proveedor, prefix="direcciones")
        telefonos = TelefonoFormSet(request.POST, instance=proveedor, prefix="telefonos")
        if form.is_valid() and direcciones.is_valid() and telefonos.is_valid():
            proveedor = form.save()
            direcciones.instance = proveedor
            direcciones.save()
            telefonos.instance = proveedor
            telefonos.save()
            messages.success(request, "Proveedor guardado correctamente.")
            return redirect("proveedores:list")
        return render(request, self.template_name, {
            "form": form, "direcciones": direcciones, "telefonos": telefonos, "object": proveedor,
        })


class ProveedorToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        proveedor = get_object_or_404(Proveedor, pk=pk)
        proveedor.activo = not proveedor.activo
        proveedor.save(update_fields=["activo"])
        messages.success(request, f"Proveedor {'activado' if proveedor.activo else 'desactivado'}.")
        return redirect("proveedores:list")


def buscar_proveedores(request):
    from django.http import JsonResponse
    q = request.GET.get("q", "")
    resultados = []
    if len(q) >= 2:
        proveedores = Proveedor.objects.filter(nombre__icontains=q, activo=True)[:15]
        for p in proveedores:
            resultados.append({
                "id": p.id, "nombre": p.nombre, "nit_documento": p.nit_documento,
            })
    return JsonResponse({"resultados": resultados})

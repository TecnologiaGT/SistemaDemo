from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from .models import Cliente
from .forms import ClienteForm, DireccionFormSet, TelefonoFormSet


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/list.html"
    context_object_name = "clientes"
    ordering = ["nombre"]
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs


class ClienteFormView(LoginRequiredMixin, View):
    template_name = "clientes/form.html"

    def get_object(self, pk):
        return get_object_or_404(Cliente, pk=pk) if pk else None

    def get(self, request, pk=None):
        cliente = self.get_object(pk)
        form = ClienteForm(instance=cliente)
        direcciones = DireccionFormSet(instance=cliente, prefix="direcciones")
        telefonos = TelefonoFormSet(instance=cliente, prefix="telefonos")
        return render(request, self.template_name, {
            "form": form, "direcciones": direcciones, "telefonos": telefonos, "object": cliente,
        })

    def post(self, request, pk=None):
        cliente = self.get_object(pk)
        form = ClienteForm(request.POST, instance=cliente)
        direcciones = DireccionFormSet(request.POST, instance=cliente, prefix="direcciones")
        telefonos = TelefonoFormSet(request.POST, instance=cliente, prefix="telefonos")
        if form.is_valid() and direcciones.is_valid() and telefonos.is_valid():
            cliente = form.save()
            direcciones.instance = cliente
            direcciones.save()
            telefonos.instance = cliente
            telefonos.save()
            messages.success(request, "Cliente guardado correctamente.")
            return redirect("clientes:list")
        return render(request, self.template_name, {
            "form": form, "direcciones": direcciones, "telefonos": telefonos, "object": cliente,
        })


class ClienteToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.activo = not cliente.activo
        cliente.save(update_fields=["activo"])
        messages.success(request, f"Cliente {'activado' if cliente.activo else 'desactivado'}.")
        return redirect("clientes:list")


def buscar_clientes(request):
    """Endpoint JSON usado por el buscador rápido (Shift+F12) en Caja: busca
    por nombre o por teléfono."""
    from django.db.models import Q
    from django.http import JsonResponse
    q = request.GET.get("q", "")
    resultados = []
    if len(q) >= 2:
        clientes = (
            Cliente.objects.filter(Q(nombre__icontains=q) | Q(telefonos__telefono__icontains=q), activo=True)
            .distinct()[:15]
        )
        for c in clientes:
            telefono = c.telefonos.first()
            resultados.append({
                "id": c.id,
                "nombre": c.nombre,
                "nit_documento": c.nit_documento,
                "telefono": telefono.telefono if telefono else "",
            })
    return JsonResponse({"resultados": resultados})

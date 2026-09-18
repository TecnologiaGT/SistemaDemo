from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View

from .models import Tienda, Empleado
from .forms import TiendaForm, EmpleadoForm
from .permissions import usuario_es_admin, AdminRequiredMixin

MODULOS = [
    {"nombre": "Vender", "icono": "🧾", "url": "ventas:caja"},
    {"nombre": "Clientes", "icono": "🧑‍🤝‍🧑", "url": "clientes:list"},
    {"nombre": "Ventas Registradas", "icono": "📄", "url": "ventas:list"},
    {"nombre": "Devolución de Venta", "icono": "↩️", "url": "ventas:devolucion"},
    {"nombre": "Comprar", "icono": "🛒", "url": "compras:create"},
    {"nombre": "Proveedores", "icono": "🚚", "url": "proveedores:list"},
    {"nombre": "Compras Registradas", "icono": "📋", "url": "compras:list"},
    {"nombre": "Productos", "icono": "📦", "url": "productos:list"},
    {"nombre": "Inventario", "icono": "🏬", "url": "inventario:list"},
    {"nombre": "Traspasos", "icono": "🔁", "url": "inventario:traspaso_list"},
    {"nombre": "Tiendas", "icono": "🏪", "url": "core:tienda_list"},
    {"nombre": "Empleados", "icono": "🪪", "url": "core:empleado_list", "solo_admin": True},
]


@login_required
def dashboard(request):
    es_admin = usuario_es_admin(request.user)
    modulos = [m for m in MODULOS if not m.get("solo_admin") or es_admin]
    return render(request, "core/dashboard.html", {"modulos": modulos})


# --- Tiendas ---
class TiendaListView(LoginRequiredMixin, ListView):
    model = Tienda
    template_name = "core/tienda_list.html"
    context_object_name = "tiendas"
    ordering = ["nombre"]


class TiendaCreateView(LoginRequiredMixin, CreateView):
    model = Tienda
    form_class = TiendaForm
    template_name = "core/tienda_form.html"
    success_url = reverse_lazy("core:tienda_list")

    def form_valid(self, form):
        messages.success(self.request, "Tienda guardada correctamente.")
        return super().form_valid(form)


class TiendaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tienda
    form_class = TiendaForm
    template_name = "core/tienda_form.html"
    success_url = reverse_lazy("core:tienda_list")

    def form_valid(self, form):
        messages.success(self.request, "Tienda actualizada correctamente.")
        return super().form_valid(form)


class TiendaToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tienda = get_object_or_404(Tienda, pk=pk)
        tienda.activa = not tienda.activa
        tienda.save(update_fields=["activa"])
        messages.success(request, f"Tienda {'activada' if tienda.activa else 'desactivada'}.")
        return redirect("core:tienda_list")


# --- Empleados (y sus usuarios del sistema) ---
# Solo administradores pueden ver/crear/editar empleados, porque aquí es donde
# se maneja el usuario, la contraseña y el tipo de permiso de cada quien.

def _guardar_usuario_empleado(empleado, form):
    """Crea o actualiza el User de Django asociado al empleado, a partir de
    los campos username/password/tipo_usuario del formulario."""
    username = form.cleaned_data.get("username")
    password = form.cleaned_data.get("password")
    es_admin = form.cleaned_data.get("tipo_usuario") == "admin"

    if not username:
        return  # este empleado no tiene (o no tendrá) usuario de sistema

    if empleado.usuario_id:
        user = empleado.usuario
        user.username = username
        user.is_staff = es_admin
        if password:
            user.set_password(password)
        user.save()
    else:
        user = User(username=username, is_staff=es_admin)
        user.set_password(password) if password else user.set_unusable_password()
        user.save()
        empleado.usuario = user
        empleado.save(update_fields=["usuario"])


class EmpleadoListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Empleado
    template_name = "core/empleado_list.html"
    context_object_name = "empleados"
    ordering = ["nombre"]


class EmpleadoCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "core/empleado_form.html"
    success_url = reverse_lazy("core:empleado_list")

    def form_valid(self, form):
        empleado = form.save()
        _guardar_usuario_empleado(empleado, form)
        messages.success(self.request, "Empleado guardado correctamente.")
        return redirect(self.success_url)


class EmpleadoUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "core/empleado_form.html"
    success_url = reverse_lazy("core:empleado_list")

    def form_valid(self, form):
        empleado = form.save()
        _guardar_usuario_empleado(empleado, form)
        messages.success(self.request, "Empleado actualizado correctamente.")
        return redirect(self.success_url)


class EmpleadoToggleView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        empleado = get_object_or_404(Empleado, pk=pk)
        empleado.activo = not empleado.activo
        empleado.save(update_fields=["activo"])
        messages.success(request, f"Empleado {'activado' if empleado.activo else 'desactivado'}.")
        return redirect("core:empleado_list")

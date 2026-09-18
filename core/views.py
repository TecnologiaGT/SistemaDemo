from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from PIL import Image

from .models import Tienda, Empleado, Personalizacion
from .forms import TiendaForm, EmpleadoForm, PersonalizacionForm
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
    {"nombre": "Personalización", "icono": "🎨", "url": "core:personalizacion", "solo_admin": True},
]


@login_required
def dashboard(request):
    es_admin = usuario_es_admin(request.user)
    modulos = [m for m in MODULOS if not m.get("solo_admin") or es_admin]
    config = Personalizacion.obtener()
    return render(request, "core/dashboard.html", {
        "modulos": modulos,
        "tiene_foto_fondo": bool(config.foto_fondo),
    })


# --- Personalización (foto de fondo del menú + paleta de colores) ---
# Solo administradores pueden cambiarla; la ven todos los usuarios.

_ANCHO_MAXIMO_FOTO = 1920


def _comprimir_foto(archivo_subido):
    """Convierte la imagen subida a JPEG, la reduce a un ancho máximo
    razonable, y devuelve (bytes, content_type) listos para guardar en la
    base de datos."""
    imagen = Image.open(archivo_subido)
    imagen = imagen.convert("RGB")
    if imagen.width > _ANCHO_MAXIMO_FOTO:
        alto_nuevo = int(imagen.height * (_ANCHO_MAXIMO_FOTO / imagen.width))
        imagen = imagen.resize((_ANCHO_MAXIMO_FOTO, alto_nuevo), Image.LANCZOS)
    buffer = BytesIO()
    imagen.save(buffer, format="JPEG", quality=82, optimize=True)
    return buffer.getvalue(), "image/jpeg"


class PersonalizacionView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = "core/personalizacion_form.html"

    def get(self, request):
        config = Personalizacion.obtener()
        form = PersonalizacionForm(initial={"paleta": config.paleta})
        return render(request, self.template_name, {"form": form, "config": config})

    def post(self, request):
        config = Personalizacion.obtener()
        form = PersonalizacionForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "config": config})

        config.paleta = form.cleaned_data["paleta"]
        foto = form.cleaned_data.get("foto")
        if foto:
            config.foto_fondo, config.foto_fondo_tipo = _comprimir_foto(foto)
        elif form.cleaned_data.get("quitar_foto"):
            config.foto_fondo = None
            config.foto_fondo_tipo = ""
        config.save()
        messages.success(request, "Personalización guardada correctamente.")
        return redirect("core:personalizacion")


class PersonalizacionFotoView(LoginRequiredMixin, View):
    def get(self, request):
        config = Personalizacion.obtener()
        if not config.foto_fondo:
            raise Http404
        return HttpResponse(
            bytes(config.foto_fondo), content_type=config.foto_fondo_tipo or "image/jpeg"
        )


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
        if empleado.activo and empleado.tipo_usuario == "admin":
            otros_admins = (
                Empleado.objects.filter(tipo_usuario="admin", activo=True)
                .exclude(pk=empleado.pk)
                .exists()
            )
            if not otros_admins:
                messages.error(request, "No puedes desactivar al único administrador activo del sistema.")
                return redirect("core:empleado_list")
        empleado.activo = not empleado.activo
        empleado.save(update_fields=["activo"])
        messages.success(request, f"Empleado {'activado' if empleado.activo else 'desactivado'}.")
        return redirect("core:empleado_list")

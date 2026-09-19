from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, View
from PIL import Image

from .models import Tienda, Empleado, Personalizacion, SnapshotDemo
from .forms import TiendaForm, EmpleadoForm, PersonalizacionForm
from .permissions import usuario_es_admin, usuario_es_superusuario_oculto, AdminRequiredMixin
from . import snapshot_demo
from .catalogo_productos import renombrar_productos_segun_tipo

MODULOS = [
    {"nombre": "Vender", "icono": "💰", "url": "ventas:caja"},
    {"nombre": "Clientes", "icono": "🤝", "url": "clientes:list"},
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
    {"nombre": "Consultas y Reportes", "icono": "📊", "url": "reportes:menu", "solo_admin": True},
    {"nombre": "Personalización", "icono": "🎨", "url": "core:personalizacion", "solo_admin": True},
]


@login_required
def dashboard(request):
    es_admin = usuario_es_admin(request.user)
    modulos = [m for m in MODULOS if not m.get("solo_admin") or es_admin]
    config = Personalizacion.obtener()
    contexto = {
        "modulos": modulos,
        "tiene_foto_fondo": bool(config.foto_fondo),
        "es_superusuario_oculto": usuario_es_superusuario_oculto(request.user),
        "tipos_sistema": Personalizacion.TIPOS_SISTEMA,
    }
    if contexto["es_superusuario_oculto"]:
        foto = SnapshotDemo.obtener()
        contexto["snapshot_guardado"] = bool(foto.datos)
        contexto["snapshot_fecha"] = foto.creado
    return render(request, "core/dashboard.html", contexto)


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


class ReiniciarSistemaView(LoginRequiredMixin, View):
    """Solo para el superusuario "oculto" (ver usuario_es_superusuario_oculto):
    cambiar la contraseña del usuario "admin" y cambiar el tipo de sistema
    de la demo. No usa AdminRequiredMixin a propósito: un administrador
    normal (como "admin") NO debe poder llegar aquí ni por URL directa."""

    def post(self, request):
        if not usuario_es_superusuario_oculto(request.user):
            messages.error(request, "No tienes permiso para esta acción.")
            return redirect("core:home")

        accion = request.POST.get("accion")

        if accion == "password_admin":
            nueva = request.POST.get("nueva_password", "")
            confirmar = request.POST.get("confirmar_password", "")
            if len(nueva) < 8:
                messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
            elif nueva != confirmar:
                messages.error(request, "Las dos contraseñas no coinciden.")
            else:
                admin_user = User.objects.filter(username="admin").first()
                if admin_user:
                    admin_user.set_password(nueva)
                    admin_user.save()
                    messages.success(request, "Contraseña de \"admin\" actualizada correctamente.")
                else:
                    messages.error(request, "No se encontró ningún usuario \"admin\".")

        elif accion == "tipo_sistema":
            tipo = request.POST.get("tipo_sistema")
            validos = dict(Personalizacion.TIPOS_SISTEMA)
            if tipo in validos:
                config = Personalizacion.obtener()
                config.tipo_sistema = tipo
                config.save(update_fields=["tipo_sistema"])
                renombrar_productos_segun_tipo(tipo)
                messages.success(request, f"Tipo de sistema cambiado a {validos[tipo]}.")
            else:
                messages.error(request, "Tipo de sistema inválido.")

        elif accion == "guardar_snapshot":
            foto = SnapshotDemo.obtener()
            foto.datos = snapshot_demo.construir_snapshot()
            foto.creado = timezone.now()
            foto.save(update_fields=["datos", "creado", "actualizado"])
            messages.success(
                request,
                "Estado actual guardado. Desde ahora, \"Restaurar datos\" volverá exactamente a este punto.",
            )

        elif accion == "restaurar_datos":
            foto = SnapshotDemo.obtener()
            if not foto.datos:
                messages.error(
                    request,
                    "Todavía no hay ningún estado guardado. Usa primero \"Guardar estado actual\".",
                )
                return redirect("core:home")
            try:
                snapshot_demo.restaurar_snapshot(foto.datos)
            except Exception as error:
                messages.error(request, f"No se pudo restaurar: {error}")
                return redirect("core:home")

            # Los nombres de los productos guardados en la foto son los que
            # tenía el tipo de sistema activo cuando se guardó (por ejemplo
            # "Librería"). Después de restaurar, siempre se vuelven a
            # renombrar según el tipo de sistema ACTUAL, para que no
            # aparezcan mezclados con el tipo que tengas elegido ahora.
            renombrar_productos_segun_tipo(Personalizacion.obtener().tipo_sistema)

            nueva_password = snapshot_demo.generar_password_aleatoria()
            admin_user = User.objects.filter(username="admin").first()
            if admin_user:
                admin_user.set_password(nueva_password)
                admin_user.save()
                messages.success(
                    request,
                    f"Datos restaurados correctamente. Nueva contraseña de \"admin\": {nueva_password}",
                )
            else:
                messages.warning(
                    request,
                    "Datos restaurados, pero no se encontró ningún usuario \"admin\" para asignarle contraseña nueva.",
                )

        else:
            messages.error(request, "Acción no reconocida.")

        return redirect("core:home")


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

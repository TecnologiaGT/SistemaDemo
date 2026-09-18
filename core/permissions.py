from django.contrib import messages
from django.shortcuts import redirect


def usuario_es_admin(user):
    """True si el usuario logueado tiene permisos de administrador:
    superusuario de Django, o un Empleado con tipo_usuario='admin'."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    empleado = getattr(user, "empleado", None)
    return bool(empleado and empleado.tipo_usuario == "admin")


class AdminRequiredMixin:
    """Restringe una vista a usuarios con permiso de administrador.
    Usar junto con LoginRequiredMixin (LoginRequiredMixin primero en el MRO)."""

    mensaje_permiso = "No tienes permiso para acceder a esta sección."

    def dispatch(self, request, *args, **kwargs):
        if not usuario_es_admin(request.user):
            messages.error(request, self.mensaje_permiso)
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

from django import forms
from django.contrib.auth.models import User
from .models import Tienda, Empleado
from .paletas import OPCIONES_PALETA


class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = ["nombre", "direccion", "telefono", "activa"]


class EmpleadoForm(forms.ModelForm):
    username = forms.CharField(
        label="Usuario del sistema", required=False,
        help_text="Déjalo vacío si este empleado no va a iniciar sesión en el sistema.",
    )
    password = forms.CharField(
        label="Contraseña", required=False, widget=forms.PasswordInput(render_value=False),
        help_text="Déjala vacía para no cambiarla (o si el empleado no tiene usuario).",
    )

    class Meta:
        model = Empleado
        fields = ["nombre", "puesto", "telefono", "tienda", "tipo_usuario", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.usuario_id:
            self.fields["username"].initial = self.instance.usuario.username

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if username:
            qs = User.objects.filter(username=username)
            if self.instance and self.instance.pk and self.instance.usuario_id:
                qs = qs.exclude(pk=self.instance.usuario_id)
            if qs.exists():
                raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        password = cleaned.get("password")
        creando = not (self.instance and self.instance.pk and self.instance.usuario_id)
        if creando and password and not username:
            self.add_error("username", "Escribe un nombre de usuario para poder asignar contraseña.")

        # Siempre debe quedar al menos un administrador activo en el sistema.
        if self.instance and self.instance.pk:
            era_admin_activo = self.instance.tipo_usuario == "admin" and self.instance.activo
            seria_admin_activo = cleaned.get("tipo_usuario") == "admin" and cleaned.get("activo")
            if era_admin_activo and not seria_admin_activo:
                otros_admins = (
                    Empleado.objects.filter(tipo_usuario="admin", activo=True)
                    .exclude(pk=self.instance.pk)
                    .exists()
                )
                if not otros_admins:
                    self.add_error(
                        None,
                        "Debe existir al menos un administrador activo. Asigna el rol de "
                        "administrador a otro empleado antes de quitárselo a este, o de desactivarlo.",
                    )
        return cleaned


class PersonalizacionForm(forms.Form):
    paleta = forms.ChoiceField(label="Paleta de colores", choices=OPCIONES_PALETA)
    foto = forms.ImageField(
        label="Foto de fondo (pantalla de menú)", required=False,
        help_text="Se usa solo en la pantalla principal de menús. Máximo 8 MB.",
    )
    quitar_foto = forms.BooleanField(
        label="Quitar la foto de fondo actual", required=False,
    )

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto and foto.size > 8 * 1024 * 1024:
            raise forms.ValidationError("La imagen es muy grande. El máximo permitido es 8 MB.")
        return foto

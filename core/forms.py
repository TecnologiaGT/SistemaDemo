from django import forms
from django.contrib.auth.models import User
from .models import Tienda, Empleado


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
        return cleaned

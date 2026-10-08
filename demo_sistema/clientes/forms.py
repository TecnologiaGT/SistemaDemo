from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, ClienteDireccion, ClienteTelefono


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "nit_documento", "email", "activo"]


DireccionFormSet = inlineformset_factory(
    Cliente, ClienteDireccion,
    fields=["direccion", "referencia", "principal"],
    extra=1, can_delete=True,
)

TelefonoFormSet = inlineformset_factory(
    Cliente, ClienteTelefono,
    fields=["telefono", "etiqueta"],
    extra=1, can_delete=True,
)

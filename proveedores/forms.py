from django import forms
from django.forms import inlineformset_factory
from .models import Proveedor, ProveedorDireccion, ProveedorTelefono


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "nit_documento", "email", "contacto", "activo"]


DireccionFormSet = inlineformset_factory(
    Proveedor, ProveedorDireccion,
    fields=["direccion", "referencia", "principal"],
    extra=1, can_delete=True,
)

TelefonoFormSet = inlineformset_factory(
    Proveedor, ProveedorTelefono,
    fields=["telefono", "etiqueta"],
    extra=1, can_delete=True,
)

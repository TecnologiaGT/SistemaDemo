from django import forms
from .models import Tienda, Empleado


class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = ["nombre", "direccion", "telefono", "activa"]


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ["nombre", "puesto", "telefono", "tienda", "activo"]

from django.contrib import admin
from .models import Cliente, ClienteDireccion, ClienteTelefono


class ClienteDireccionInline(admin.TabularInline):
    model = ClienteDireccion
    extra = 1


class ClienteTelefonoInline(admin.TabularInline):
    model = ClienteTelefono
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit_documento", "email", "activo")
    search_fields = ("nombre", "nit_documento")
    inlines = [ClienteDireccionInline, ClienteTelefonoInline]

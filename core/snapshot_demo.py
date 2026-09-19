"""Guardar y restaurar una "foto" de los datos de demo.

Usado por el panel "Reiniciar Sistema" (ver core.views.ReiniciarSistemaView):
un superusuario oculto puede guardar el estado actual de las tablas de
negocio (clientes, proveedores, productos, ventas, compras, inventario,
traspasos, tiendas, empleados) y luego, en cualquier momento, restaurar
exactamente ese estado -por ejemplo después de que un cliente probó el
sistema y agregó/editó/borró cosas durante una demo.

A propósito NO usa django.core.management.call_command("dumpdata"/"loaddata")
sino las funciones de más bajo nivel django.core.serializers.serialize /
deserialize directamente: así no se parece a un "ejecutor de comandos" de
propósito general, solo hace esta única cosa.
"""
import secrets
import string

from django.contrib.auth.models import User
from django.core import serializers
from django.core.management.color import no_style
from django.db import connections, router, transaction
from django.utils import timezone

from clientes.models import Cliente, ClienteDireccion, ClienteTelefono
from compras.models import Compra, CompraDetalle
from core.models import Empleado, Personalizacion, Tienda
from inventario.models import Inventario, Traspaso, TraspasoDetalle
from productos.models import Producto
from proveedores.models import Proveedor, ProveedorDireccion, ProveedorTelefono
from ventas.models import Venta, VentaDetalle

# Estas cuentas nunca se tocan: no se incluyen en la foto ni se borran al
# restaurar. "walde" es el superusuario oculto de mantenimiento; "admin" es
# el usuario administrador visible de la demo (su contraseña se maneja por
# separado, con el otro botón del panel).
USUARIOS_PROTEGIDOS = {"walde", "admin"}

# Orden de guardado / borrado. Al restaurar se borra en orden inverso
# (hijos antes que padres, para respetar las relaciones on_delete=PROTECT)
# y se vuelve a crear en este mismo orden (padres antes que hijos).
# ProductoFoto se deja fuera a propósito: es una función que no se usa en
# la demo y sus archivos no sobreviven en el disco temporal de Render.
_MODELOS = [
    Personalizacion,
    Tienda,
    User,  # solo los usuarios ligados a un Empleado; ver _usuarios_de_empleados()
    Empleado,
    Cliente, ClienteDireccion, ClienteTelefono,
    Proveedor, ProveedorDireccion, ProveedorTelefono,
    Producto,
    Inventario,
    Venta, VentaDetalle,
    Compra, CompraDetalle,
    Traspaso, TraspasoDetalle,
]


def _usuarios_de_empleados():
    return User.objects.filter(empleado__isnull=False).exclude(username__in=USUARIOS_PROTEGIDOS)


def _queryset_de(modelo):
    if modelo is User:
        return _usuarios_de_empleados()
    return modelo.objects.all()


def construir_snapshot():
    """Devuelve los datos actuales de todas las tablas de negocio, como un
    texto JSON listo para guardar en SnapshotDemo.datos (TextField)."""
    objetos = []
    for modelo in _MODELOS:
        objetos.extend(_queryset_de(modelo))
    return serializers.serialize("json", objetos)


def restaurar_snapshot(datos):
    """Borra los datos actuales de negocio y los reemplaza exactamente por
    los guardados en `datos` (tal como lo devuelve construir_snapshot)."""
    if not datos:
        raise ValueError("Todavía no hay ninguna foto guardada.")

    conexion = connections[router.db_for_write(Tienda)]
    with transaction.atomic(using=conexion.alias):
        with conexion.constraint_checks_disabled():
            for modelo in reversed(_MODELOS):
                if modelo is User:
                    _usuarios_de_empleados().delete()
                else:
                    modelo.objects.all().delete()
            for objeto in serializers.deserialize("json", datos):
                objeto.save(using=conexion.alias)
        conexion.check_constraints()

    # Después de restaurar filas con PK explícita, hay que reacomodar las
    # secuencias de autoincremento (en Postgres) para que el próximo
    # registro nuevo no choque con uno restaurado.
    with conexion.cursor() as cursor:
        sql = conexion.ops.sequence_reset_sql(no_style(), _MODELOS)
        for instruccion in sql:
            cursor.execute(instruccion)


def generar_password_aleatoria(longitud=12):
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(longitud))

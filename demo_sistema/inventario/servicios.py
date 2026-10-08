"""Ajuste seguro del inventario (existencia de un producto en una tienda).

Antes, cada app (ventas/compras/inventario) tenía su propia función
`_ajustar_inventario` que hacía un simple "leer -> sumar -> guardar" sin
ningún bloqueo. Eso es una condición de carrera clásica: si dos personas
venden el mismo producto al mismo tiempo desde computadoras distintas,
ambas pueden leer la misma existencia (por ejemplo 5), cada una restar su
cantidad y guardar su propio resultado -la segunda escritura "gana" y pisa
a la primera, así que se puede vender más de lo que realmente había sin
que el sistema se dé cuenta.

Esta versión centralizada corrige eso con select_for_update(): bloquea la
fila de Inventario mientras dura el ajuste, así que si dos ventas del
mismo producto llegan al mismo tiempo, la base de datos las pone en fila
(la segunda espera a que la primera termine) y cada una ve el número ya
actualizado por la anterior. Esto lo hace la base de datos (Postgres en
producción), no Python, así que funciona sin importar cuántas
computadoras/pestañas estén vendiendo a la vez.

IMPORTANTE: ajustar_inventario() debe llamarse siempre dentro de un
`with transaction.atomic():`, porque select_for_update() lo exige.
"""
from .models import Inventario


class StockInsuficiente(Exception):
    """Se lanza cuando no alcanza el inventario para completar una venta o
    un traspaso. La vista debe capturarla y cancelar TODA la operación
    (venta/traspaso completo), no solo la línea que falló."""

    def __init__(self, producto, disponible, solicitado):
        self.producto = producto
        self.disponible = disponible
        self.solicitado = solicitado
        super().__init__(
            f'No hay suficiente existencia de "{producto}": quedan {disponible}, se intentaron sacar {solicitado}.'
        )


def ajustar_inventario(tienda, producto, delta, *, validar_existencia=False):
    """Suma `delta` (positivo o negativo) a la existencia de `producto` en
    `tienda`, de forma segura ante ventas/traspasos simultáneos.

    validar_existencia=True (se usa al vender y al traspasar, donde delta
    es negativo): si no alcanza el inventario, NO se guarda ningún cambio
    y se lanza StockInsuficiente. En compras, anulaciones y devoluciones
    (donde solo se devuelve/agrega inventario) no hace falta validar.

    Devuelve la existencia final ya guardada."""
    Inventario.objects.get_or_create(tienda=tienda, producto=producto)
    # select_for_update() bloquea esta fila hasta que termine la
    # transacción actual: cualquier otra venta/compra/traspaso del mismo
    # producto en la misma tienda tiene que esperar su turno aquí.
    inv = Inventario.objects.select_for_update().get(tienda=tienda, producto=producto)

    nueva_existencia = inv.existencia + delta
    if validar_existencia and nueva_existencia < 0:
        raise StockInsuficiente(producto, inv.existencia, -delta)

    inv.existencia = max(0, nueva_existencia)
    inv.save(update_fields=["existencia"])
    return inv.existencia

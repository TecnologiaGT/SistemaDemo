import calendar
import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from clientes.models import Cliente
from compras.models import Compra, CompraDetalle
from core.models import Empleado, Tienda
from inventario.models import Inventario
from productos.models import Producto
from proveedores.models import Proveedor
from ventas.models import Venta, VentaDetalle

# Julio, agosto y septiembre de 2026.
ANIO = 2026
MESES = [7, 8, 9]
COMPRAS_POR_MES = 4
VENTAS_POR_MES = 20


def _ajustar_inventario(tienda, producto, delta):
    """Igual que _ajustar_inventario en compras/ventas: suma `delta` a la
    existencia sin dejarla bajar de 0. Usar exactamente esta lógica es lo
    que garantiza que el inventario final "cuadre" con el historial que
    se genera aquí."""
    inv, _ = Inventario.objects.get_or_create(tienda=tienda, producto=producto)
    inv.existencia = max(0, inv.existencia + delta)
    inv.save(update_fields=["existencia"])


class Command(BaseCommand):
    help = (
        "Genera compras (usuarios administrador) y ventas (distintas tiendas y "
        "vendedores) de demostración para julio, agosto y septiembre de 2026. "
        "Procesa los movimientos en orden cronológico y nunca vende más "
        "existencia de la disponible en ese momento, así que el inventario "
        "final queda respaldado por este historial."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Generar los movimientos aunque ya existan compras o ventas en ese período.",
        )

    def handle(self, *args, **options):
        rng = random.Random(20260701)  # semilla fija: mismo resultado cada vez que se corre

        ya_existen = (
            Venta.objects.filter(fecha__year=ANIO, fecha__month__in=MESES).exists()
            or Compra.objects.filter(fecha__year=ANIO, fecha__month__in=MESES).exists()
        )
        if ya_existen and not options["force"]:
            self.stdout.write(self.style.WARNING(
                "Ya existen compras o ventas registradas en julio-septiembre de 2026. "
                "No se generó nada nuevo para no duplicar. Si de verdad quieres agregar "
                "más encima de esas, vuelve a correr el comando con --force."
            ))
            return

        tiendas = list(Tienda.objects.filter(activa=True))
        if not tiendas:
            self.stdout.write(self.style.ERROR("No hay tiendas activas. Corre primero seed_demo."))
            return

        admins = list(Empleado.objects.filter(activo=True, tipo_usuario="admin"))
        if not admins:
            self.stdout.write(self.style.ERROR(
                "No hay empleados con tipo de usuario Administrador. No se pueden registrar compras."
            ))
            return

        vendedores_por_tienda = {}
        for t in tiendas:
            vends = list(Empleado.objects.filter(activo=True, tipo_usuario="empleado", tienda=t))
            if vends:
                vendedores_por_tienda[t.id] = vends
        tiendas_con_vendedor = [t for t in tiendas if t.id in vendedores_por_tienda]
        if not tiendas_con_vendedor:
            self.stdout.write(self.style.ERROR(
                "Ninguna tienda tiene vendedores asignados (Empleados con tipo Empleado y "
                "una tienda asignada). Asigna al menos uno antes de correr este comando."
            ))
            return
        tiendas_sin_vendedor = [t for t in tiendas if t.id not in vendedores_por_tienda]
        if tiendas_sin_vendedor:
            nombres = ", ".join(t.nombre for t in tiendas_sin_vendedor)
            self.stdout.write(self.style.WARNING(
                f"Aviso: estas tiendas no tienen vendedor asignado y no recibirán ventas: {nombres}."
            ))

        proveedores = list(Proveedor.objects.filter(activo=True))
        if not proveedores:
            self.stdout.write(self.style.ERROR("No hay proveedores activos. No se pueden registrar compras."))
            return

        clientes = list(Cliente.objects.filter(activo=True))
        productos = list(Producto.objects.filter(activo=True))
        if not productos:
            self.stdout.write(self.style.ERROR("No hay productos activos."))
            return

        hoy = timezone.localdate()

        # --- 1) Armar la lista de eventos (compra/venta) con su fecha y sus
        # participantes, repartiendo tiendas/vendedores/administradores por
        # turnos para que ningún mes se concentre siempre en los mismos. ---
        eventos = []
        for mes in MESES:
            if ANIO > hoy.year or (ANIO == hoy.year and mes > hoy.month):
                continue  # mes futuro: no se genera (evitamos fechas por venir)
            dia_max = hoy.day if (ANIO == hoy.year and mes == hoy.month) else calendar.monthrange(ANIO, mes)[1]
            if dia_max < 1:
                continue

            tiendas_compra = tiendas[:]
            rng.shuffle(tiendas_compra)
            admins_mes = admins[:]
            rng.shuffle(admins_mes)
            proveedores_mes = proveedores[:]
            rng.shuffle(proveedores_mes)
            for i in range(COMPRAS_POR_MES):
                dia = rng.randint(1, dia_max)
                fecha = timezone.make_aware(datetime(ANIO, mes, dia, rng.randint(8, 18), rng.randint(0, 59)))
                eventos.append({
                    "tipo": "compra",
                    "fecha": fecha,
                    "tienda": tiendas_compra[i % len(tiendas_compra)],
                    "empleado": admins_mes[i % len(admins_mes)],
                    "proveedor": proveedores_mes[i % len(proveedores_mes)],
                })

            tiendas_venta = tiendas_con_vendedor[:]
            rng.shuffle(tiendas_venta)
            for i in range(VENTAS_POR_MES):
                tienda = tiendas_venta[i % len(tiendas_venta)]
                vendedor = rng.choice(vendedores_por_tienda[tienda.id])
                cliente = rng.choice(clientes) if clientes and rng.random() < 0.75 else None
                dia = rng.randint(1, dia_max)
                fecha = timezone.make_aware(datetime(ANIO, mes, dia, rng.randint(8, 20), rng.randint(0, 59)))
                eventos.append({
                    "tipo": "venta",
                    "fecha": fecha,
                    "tienda": tienda,
                    "empleado": vendedor,
                    "cliente": cliente,
                })

        # --- 2) Procesar en orden cronológico, para que cada venta solo use
        # existencia que ya llegó con una compra anterior (o venía de antes). ---
        eventos.sort(key=lambda e: e["fecha"])

        total_compras = total_ventas = ventas_omitidas = 0

        for ev in eventos:
            if ev["tipo"] == "compra":
                tienda = ev["tienda"]
                compra = Compra.objects.create(
                    estado="V", tienda=tienda, proveedor=ev["proveedor"], empleado=ev["empleado"]
                )
                n_lineas = rng.randint(2, 5)
                for producto in rng.sample(productos, min(n_lineas, len(productos))):
                    cantidad = rng.randint(15, 40)
                    CompraDetalle.objects.create(
                        compra=compra, producto=producto,
                        cantidad=cantidad, precio_unitario=producto.precio_compra,
                    )
                    _ajustar_inventario(tienda, producto, cantidad)
                compra.recalcular_total()
                Compra.objects.filter(pk=compra.pk).update(fecha=ev["fecha"])
                total_compras += 1

            else:
                tienda = ev["tienda"]
                candidatos = rng.sample(productos, len(productos))
                objetivo_lineas = rng.randint(1, 4)
                lineas = []
                for producto in candidatos:
                    inv = Inventario.objects.filter(tienda=tienda, producto=producto).first()
                    disponible = inv.existencia if inv else 0
                    if disponible <= 0:
                        continue
                    cantidad = rng.randint(1, min(5, disponible))
                    lineas.append((producto, cantidad))
                    if len(lineas) >= objetivo_lineas:
                        break

                if not lineas:
                    ventas_omitidas += 1
                    continue

                venta = Venta.objects.create(
                    tipo="V", estado="V", tienda=tienda, empleado=ev["empleado"], cliente=ev.get("cliente")
                )
                for producto, cantidad in lineas:
                    VentaDetalle.objects.create(
                        venta=venta, producto=producto,
                        cantidad=cantidad, precio_unitario=producto.precio_venta,
                    )
                    _ajustar_inventario(tienda, producto, -cantidad)
                venta.recalcular_total()
                Venta.objects.filter(pk=venta.pk).update(fecha=ev["fecha"])
                total_ventas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {total_compras} compras y {total_ventas} ventas generadas entre julio y "
            f"septiembre de 2026 (el inventario quedó actualizado con cada una)."
        ))
        if ventas_omitidas:
            self.stdout.write(
                f"({ventas_omitidas} ventas planeadas se omitieron porque, en ese momento de "
                "la simulación, esa tienda no tenía existencia de ningún producto.)"
            )

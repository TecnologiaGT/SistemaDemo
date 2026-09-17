from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Tienda, Empleado
from clientes.models import Cliente, ClienteDireccion, ClienteTelefono
from proveedores.models import Proveedor, ProveedorDireccion, ProveedorTelefono
from productos.models import Producto
from inventario.models import Inventario


class Command(BaseCommand):
    help = "Crea datos de ejemplo (tiendas, empleados, clientes, proveedores, productos e inventario) para la demo."

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "Admin1234!")
            self.stdout.write(self.style.SUCCESS("Superusuario creado: admin / Admin1234!"))
        else:
            self.stdout.write("El superusuario 'admin' ya existe.")

        tienda_central, _ = Tienda.objects.get_or_create(nombre="Tienda Central", defaults={"direccion": "Zona 1, Ciudad Central", "telefono": "555-0100"})
        tienda_norte, _ = Tienda.objects.get_or_create(nombre="Sucursal Norte", defaults={"direccion": "Zona 4, Sector Norte", "telefono": "555-0200"})

        Empleado.objects.get_or_create(nombre="Ana Martínez", defaults={"puesto": "Vendedora", "tienda": tienda_central, "telefono": "5555-1111"})
        Empleado.objects.get_or_create(nombre="Carlos Pérez", defaults={"puesto": "Encargado de bodega", "tienda": tienda_norte, "telefono": "5555-2222"})

        cliente, creado = Cliente.objects.get_or_create(nombre="María López", defaults={"nit_documento": "1234567-8", "email": "maria.lopez@example.com"})
        if creado:
            ClienteDireccion.objects.create(cliente=cliente, direccion="6a avenida 12-34, Zona 1", principal=True)
            ClienteTelefono.objects.create(cliente=cliente, telefono="5555-3333", etiqueta="Celular")

        cliente2, creado2 = Cliente.objects.get_or_create(nombre="Consumidor Final", defaults={"nit_documento": "CF"})

        proveedor, creado_p = Proveedor.objects.get_or_create(nombre="Distribuidora El Sol", defaults={"nit_documento": "9876543-2", "contacto": "Lucía Ramírez"})
        if creado_p:
            ProveedorDireccion.objects.create(proveedor=proveedor, direccion="Km 15 Carretera al Pacífico", principal=True)
            ProveedorTelefono.objects.create(proveedor=proveedor, telefono="5555-4444", etiqueta="Oficina")

        productos_demo = [
            {"codigo": "P001", "nombre": "Camiseta básica", "precio_compra": 25, "precio_venta": 45},
            {"codigo": "P002", "nombre": "Pantalón de mezclilla", "precio_compra": 60, "precio_venta": 110},
            {"codigo": "P003", "nombre": "Gorra deportiva", "precio_compra": 15, "precio_venta": 30},
            {"codigo": "P004", "nombre": "Zapatos casuales", "precio_compra": 90, "precio_venta": 165},
            {"codigo": "P005", "nombre": "Chumpa impermeable", "precio_compra": 120, "precio_venta": 220},
        ]
        for pd in productos_demo:
            producto, _ = Producto.objects.get_or_create(codigo=pd["codigo"], defaults={
                "nombre": pd["nombre"], "precio_compra": pd["precio_compra"], "precio_venta": pd["precio_venta"],
            })
            Inventario.objects.get_or_create(tienda=tienda_central, producto=producto, defaults={"existencia": 25})
            Inventario.objects.get_or_create(tienda=tienda_norte, producto=producto, defaults={"existencia": 10})

        self.stdout.write(self.style.SUCCESS("Datos de demo creados correctamente."))

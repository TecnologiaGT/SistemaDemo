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
        admin_user, admin_user_creado = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True}
        )
        if admin_user_creado:
            admin_user.set_password("Admin1234!")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superusuario creado: admin / Admin1234!"))
        else:
            self.stdout.write("El superusuario 'admin' ya existe.")

        Empleado.objects.get_or_create(
            nombre="admin",
            defaults={"puesto": "Administrador", "tipo_usuario": "admin", "usuario": admin_user},
        )

        tienda_central, _ = Tienda.objects.get_or_create(nombre="Tienda Central", defaults={"direccion": "Zona 1, Ciudad Central", "telefono": "555-0100"})
        tienda_norte, _ = Tienda.objects.get_or_create(nombre="Sucursal Norte", defaults={"direccion": "Zona 4, Sector Norte", "telefono": "555-0200"})

        Empleado.objects.get_or_create(nombre="Ana Martínez", defaults={"puesto": "Vendedora", "tienda": tienda_central, "telefono": "5555-1111"})
        Empleado.objects.get_or_create(nombre="Carlos Pérez", defaults={"puesto": "Encargado de bodega", "tienda": tienda_norte, "telefono": "5555-2222"})

        cliente, creado = Cliente.objects.get_or_create(nombre="María López", defaults={"nit_documento": "1234567-8", "email": "maria.lopez@example.com"})
        if creado:
            ClienteDireccion.objects.create(cliente=cliente, direccion="6a avenida 12-34, Zona 1", principal=True)
            ClienteTelefono.objects.create(cliente=cliente, telefono="5555-3333", etiqueta="Celular")

        cliente2, creado2 = Cliente.objects.get_or_create(nombre="Consumidor Final", defaults={"nit_documento": "CF"})

        clientes_demo = [
            {"nombre": "José Ramírez", "nit_documento": "2233445-1", "telefono": "5551-0001"},
            {"nombre": "Ana Gómez", "nit_documento": "2233445-2", "telefono": "5551-0002"},
            {"nombre": "Luis Morales", "nit_documento": "2233445-3", "telefono": "5551-0003"},
            {"nombre": "Carmen Díaz", "nit_documento": "2233445-4", "telefono": "5551-0004"},
            {"nombre": "Roberto Castillo", "nit_documento": "2233445-5", "telefono": "5551-0005"},
            {"nombre": "Patricia Herrera", "nit_documento": "2233445-6", "telefono": "5551-0006"},
            {"nombre": "Fernando Ortiz", "nit_documento": "2233445-7", "telefono": "5551-0007"},
            {"nombre": "Silvia Cabrera", "nit_documento": "2233445-8", "telefono": "5551-0008"},
            {"nombre": "Miguel Ángel Rojas", "nit_documento": "2233445-9", "telefono": "5551-0009"},
            {"nombre": "Gabriela Soto", "nit_documento": "2233445-10", "telefono": "5551-0010"},
        ]
        for cd in clientes_demo:
            cli, creado_cli = Cliente.objects.get_or_create(
                nombre=cd["nombre"], defaults={"nit_documento": cd["nit_documento"]}
            )
            if creado_cli:
                ClienteTelefono.objects.create(cliente=cli, telefono=cd["telefono"], etiqueta="Celular")

        proveedor, creado_p = Proveedor.objects.get_or_create(nombre="Distribuidora El Sol", defaults={"nit_documento": "9876543-2", "contacto": "Lucía Ramírez"})
        if creado_p:
            ProveedorDireccion.objects.create(proveedor=proveedor, direccion="Km 15 Carretera al Pacífico", principal=True)
            ProveedorTelefono.objects.create(proveedor=proveedor, telefono="5555-4444", etiqueta="Oficina")

        proveedores_demo = [
            {"nombre": "Textiles del Norte", "nit_documento": "8877665-1", "contacto": "Marta Vásquez", "telefono": "5552-0001"},
            {"nombre": "Calzado Industrial S.A.", "nit_documento": "8877665-2", "contacto": "Edgar Solís", "telefono": "5552-0002"},
            {"nombre": "Importadora Maya", "nit_documento": "8877665-3", "contacto": "Rosa Ical", "telefono": "5552-0003"},
            {"nombre": "Suministros Guatemala", "nit_documento": "8877665-4", "contacto": "Hugo Estrada", "telefono": "5552-0004"},
            {"nombre": "Comercial Quetzal", "nit_documento": "8877665-5", "contacto": "Diana Paz", "telefono": "5552-0005"},
            {"nombre": "Distribuidora La Económica", "nit_documento": "8877665-6", "contacto": "Julio Recinos", "telefono": "5552-0006"},
            {"nombre": "Almacenes del Pacífico", "nit_documento": "8877665-7", "contacto": "Karla Mendoza", "telefono": "5552-0007"},
            {"nombre": "Grupo Ferretero Central", "nit_documento": "8877665-8", "contacto": "Oscar Villagrán", "telefono": "5552-0008"},
            {"nombre": "Bodegas del Altiplano", "nit_documento": "8877665-9", "contacto": "Elena Xico", "telefono": "5552-0009"},
            {"nombre": "Proveedora Los Andes", "nit_documento": "8877665-10", "contacto": "Iván Barrios", "telefono": "5552-0010"},
        ]
        for pdv in proveedores_demo:
            prov, creado_prov = Proveedor.objects.get_or_create(
                nombre=pdv["nombre"], defaults={"nit_documento": pdv["nit_documento"], "contacto": pdv["contacto"]}
            )
            if creado_prov:
                ProveedorTelefono.objects.create(proveedor=prov, telefono=pdv["telefono"], etiqueta="Oficina")

        productos_demo = [
            {"codigo": "P001", "nombre": "Camiseta básica", "precio_compra": 25, "precio_venta": 45},
            {"codigo": "P002", "nombre": "Pantalón de mezclilla", "precio_compra": 60, "precio_venta": 110},
            {"codigo": "P003", "nombre": "Gorra deportiva", "precio_compra": 15, "precio_venta": 30},
            {"codigo": "P004", "nombre": "Zapatos casuales", "precio_compra": 90, "precio_venta": 165},
            {"codigo": "P005", "nombre": "Chumpa impermeable", "precio_compra": 120, "precio_venta": 220},
            {"codigo": "P006", "nombre": "Camisa formal manga larga", "precio_compra": 40, "precio_venta": 75},
            {"codigo": "P007", "nombre": "Short deportivo", "precio_compra": 20, "precio_venta": 40},
            {"codigo": "P008", "nombre": "Sudadera con capucha", "precio_compra": 70, "precio_venta": 130},
            {"codigo": "P009", "nombre": "Cinturón de cuero", "precio_compra": 35, "precio_venta": 65},
            {"codigo": "P010", "nombre": "Calcetines (paquete x3)", "precio_compra": 10, "precio_venta": 20},
            {"codigo": "P011", "nombre": "Bufanda de lana", "precio_compra": 25, "precio_venta": 48},
            {"codigo": "P012", "nombre": "Guantes de invierno", "precio_compra": 18, "precio_venta": 35},
            {"codigo": "P013", "nombre": "Tenis para correr", "precio_compra": 150, "precio_venta": 275},
            {"codigo": "P014", "nombre": "Chaleco acolchado", "precio_compra": 95, "precio_venta": 175},
            {"codigo": "P015", "nombre": "Sombrero de ala", "precio_compra": 22, "precio_venta": 42},
        ]
        for pd in productos_demo:
            producto, _ = Producto.objects.get_or_create(codigo=pd["codigo"], defaults={
                "nombre": pd["nombre"], "precio_compra": pd["precio_compra"], "precio_venta": pd["precio_venta"],
            })
            Inventario.objects.get_or_create(tienda=tienda_central, producto=producto, defaults={"existencia": 25})
            Inventario.objects.get_or_create(tienda=tienda_norte, producto=producto, defaults={"existencia": 10})

        self.stdout.write(self.style.SUCCESS("Datos de demo creados correctamente."))

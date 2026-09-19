"""Nombres de los 15 productos de la demo, según el "Tipo de sistema"
elegido en el panel "Reiniciar Sistema".

A propósito NO se crean ni se borran productos al cambiar de tipo: los
mismos 15 códigos (P001..P015) simplemente cambian de nombre, así se
conservan intactos el inventario, las ventas y las compras ya registradas
(que apuntan al producto por su id/código, no por su nombre).
"""
from productos.models import Producto

# codigo -> nombre, uno por cada tipo de sistema (deben coincidir con las
# claves de Personalizacion.TIPOS_SISTEMA).
CATALOGO_POR_TIPO = {
    "ropa": {
        "P001": "Camiseta básica",
        "P002": "Pantalón de mezclilla",
        "P003": "Gorra deportiva",
        "P004": "Zapatos casuales",
        "P005": "Chumpa impermeable",
        "P006": "Camisa formal manga larga",
        "P007": "Short deportivo",
        "P008": "Sudadera con capucha",
        "P009": "Cinturón de cuero",
        "P010": "Calcetines (paquete x3)",
        "P011": "Bufanda de lana",
        "P012": "Guantes de invierno",
        "P013": "Tenis para correr",
        "P014": "Chaleco acolchado",
        "P015": "Sombrero de ala",
    },
    "libreria": {
        "P001": "Cuaderno universitario 100 hojas",
        "P002": "Mochila escolar",
        "P003": "Caja de lápices de colores (x12)",
        "P004": "Calculadora científica",
        "P005": "Set de reglas geométricas",
        "P006": "Lapiceros de tinta (paquete x3)",
        "P007": "Marcadores permanentes (x4)",
        "P008": "Folders tamaño carta (paquete x10)",
        "P009": "Cinta adhesiva escolar",
        "P010": "Tijeras escolares",
        "P011": "Goma en barra",
        "P012": "Sacapuntas doble",
        "P013": "Block de dibujo",
        "P014": "Resaltadores (paquete x4)",
        "P015": "Cartuchera de tela",
    },
    "farmacia": {
        "P001": "Paracetamol 500mg (caja x20)",
        "P002": "Ibuprofeno 400mg (caja x20)",
        "P003": "Amoxicilina 500mg (caja x12)",
        "P004": "Loratadina 10mg (caja x10)",
        "P005": "Omeprazol 20mg (caja x14)",
        "P006": "Vitamina C 1000mg (frasco x30)",
        "P007": "Suero oral (sobre)",
        "P008": "Alcohol en gel 250ml",
        "P009": "Curitas surtidas (caja)",
        "P010": "Jarabe para la tos 120ml",
        "P011": "Antiácido en tabletas (frasco)",
        "P012": "Complejo B (frasco x30)",
        "P013": "Gasas estériles (paquete)",
        "P014": "Termómetro digital",
        "P015": "Guantes de látex (caja x100)",
    },
    "abarroteria": {
        "P001": "Arroz (bolsa 1lb)",
        "P002": "Frijol negro (bolsa 1lb)",
        "P003": "Aceite vegetal (botella 1L)",
        "P004": "Azúcar (bolsa 2lb)",
        "P005": "Sal (bolsa 1lb)",
        "P006": "Café molido (bolsa 250g)",
        "P007": "Pasta para sopa (paquete)",
        "P008": "Atún en lata",
        "P009": "Leche en polvo (bolsa)",
        "P010": "Galletas surtidas (paquete)",
        "P011": "Refresco embotellado 2L",
        "P012": "Agua purificada 1L",
        "P013": "Jabón de lavar (barra)",
        "P014": "Papel higiénico (paquete x4)",
        "P015": "Huevos (cartón x30)",
    },
}


def renombrar_productos_segun_tipo(tipo):
    """Cambia el nombre de los productos P001..P015 según el catálogo del
    tipo de sistema dado. No crea, borra ni cambia precios/existencias:
    solo el campo `nombre`, así que ventas, compras e inventario ya
    registrados quedan intactos (siguen apuntando al mismo producto)."""
    catalogo = CATALOGO_POR_TIPO.get(tipo)
    if not catalogo:
        return
    for codigo, nombre in catalogo.items():
        Producto.objects.filter(codigo=codigo).update(nombre=nombre)

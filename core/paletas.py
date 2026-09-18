# Paletas de color predefinidas para todo el sistema.
# Cada paleta redefine las mismas variables CSS que ya existen en :root
# (static/css/styles.css), así que basta con sobreescribirlas en base.html
# según la paleta seleccionada en Personalización.

PALETAS = {
    "azul": {
        "nombre": "Azul oscuro (predeterminado)",
        "muestra": "#1b2d68",
        "variables": {
            "azul-950": "#0a1230",
            "azul-900": "#0f1a3d",
            "azul-800": "#14224f",
            "azul-700": "#1b2d68",
            "azul-600": "#24398a",
            "azul-500": "#3a52b4",
            "acento": "#4f7cff",
            "acento-2": "#7aa0ff",
            "superficie": "#101a3d",
            "superficie-2": "#14204a",
            "borde": "#263468",
        },
    },
    "verde": {
        "nombre": "Verde esmeralda",
        "muestra": "#0f5132",
        "variables": {
            "azul-950": "#07160f",
            "azul-900": "#0b2116",
            "azul-800": "#0f2c1c",
            "azul-700": "#123a24",
            "azul-600": "#155c33",
            "azul-500": "#1f7a44",
            "acento": "#2fbf71",
            "acento-2": "#6bdba0",
            "superficie": "#0e2417",
            "superficie-2": "#123a24",
            "borde": "#1f5c37",
        },
    },
    "morado": {
        "nombre": "Morado",
        "muestra": "#4a2d80",
        "variables": {
            "azul-950": "#150b28",
            "azul-900": "#1e1038",
            "azul-800": "#291748",
            "azul-700": "#382063",
            "azul-600": "#4a2d80",
            "azul-500": "#6b46b0",
            "acento": "#9265e0",
            "acento-2": "#b596ec",
            "superficie": "#1c1034",
            "superficie-2": "#291748",
            "borde": "#3d2960",
        },
    },
    "gris": {
        "nombre": "Gris / Negro",
        "muestra": "#3a3f47",
        "variables": {
            "azul-950": "#0d0f12",
            "azul-900": "#16191d",
            "azul-800": "#1f2328",
            "azul-700": "#2b3038",
            "azul-600": "#3a3f47",
            "azul-500": "#565c66",
            "acento": "#7c8792",
            "acento-2": "#a3adb6",
            "superficie": "#181b1f",
            "superficie-2": "#22262b",
            "borde": "#33383e",
        },
    },
    "vino": {
        "nombre": "Vino / Rojo oscuro",
        "muestra": "#701f2e",
        "variables": {
            "azul-950": "#1f0a0d",
            "azul-900": "#2c1014",
            "azul-800": "#3a151b",
            "azul-700": "#521d26",
            "azul-600": "#701f2e",
            "azul-500": "#9c2e40",
            "acento": "#e0435a",
            "acento-2": "#ea7d8c",
            "superficie": "#2a1216",
            "superficie-2": "#3a151b",
            "borde": "#54222a",
        },
    },
}

PALETA_DEFECTO = "azul"

OPCIONES_PALETA = [(clave, datos["nombre"]) for clave, datos in PALETAS.items()]


def variables_css(clave):
    """Devuelve las variables (nombre -> valor, sin '--') de una paleta,
    usando la paleta por defecto si la clave no existe."""
    paleta = PALETAS.get(clave, PALETAS[PALETA_DEFECTO])
    return paleta["variables"]

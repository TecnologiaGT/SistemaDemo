# Paletas de color predefinidas para todo el sistema.
# Cada paleta redefine las mismas variables CSS que ya existen en :root
# (static/css/styles.css), así que basta con sobreescribirlas en base.html
# según la paleta seleccionada en Personalización.
#
# "oscura" indica si el texto claro / textos de estado claros deben usarse
# (paletas de fondo oscuro) o si conviene texto e indicadores oscuros
# (paleta "blanco"). Los reportes con gráfica de pastel también usan este
# indicador para elegir la versión clara u oscura de sus colores.

_TEXTO_CLARO = "#eaf0ff"
_TEXTO_TENUE_CLARO = "#a9b6dd"
_EXITO_TEXTO_CLARO = "#4fe0a2"
_PELIGRO_TEXTO_CLARO = "#ff8a8e"
_ADVERTENCIA_TEXTO_CLARO = "#ffcb73"

PALETAS = {
    "azul": {
        "nombre": "Azul oscuro (predeterminado)",
        "muestra": "#1b2d68",
        "oscura": True,
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
            "texto": _TEXTO_CLARO,
            "texto-tenue": _TEXTO_TENUE_CLARO,
            "fondo-1": "#14224f",
            "fondo-2": "#0a1230",
            "campo-fondo": "#0a1230",
            "exito-texto": _EXITO_TEXTO_CLARO,
            "peligro-texto": _PELIGRO_TEXTO_CLARO,
            "advertencia-texto": _ADVERTENCIA_TEXTO_CLARO,
        },
    },
    "verde": {
        "nombre": "Verde esmeralda",
        "muestra": "#0f5132",
        "oscura": True,
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
            "texto": _TEXTO_CLARO,
            "texto-tenue": _TEXTO_TENUE_CLARO,
            "fondo-1": "#0f2c1c",
            "fondo-2": "#07160f",
            "campo-fondo": "#07160f",
            "exito-texto": _EXITO_TEXTO_CLARO,
            "peligro-texto": _PELIGRO_TEXTO_CLARO,
            "advertencia-texto": _ADVERTENCIA_TEXTO_CLARO,
        },
    },
    "morado": {
        "nombre": "Morado",
        "muestra": "#4a2d80",
        "oscura": True,
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
            "texto": _TEXTO_CLARO,
            "texto-tenue": _TEXTO_TENUE_CLARO,
            "fondo-1": "#291748",
            "fondo-2": "#150b28",
            "campo-fondo": "#150b28",
            "exito-texto": _EXITO_TEXTO_CLARO,
            "peligro-texto": _PELIGRO_TEXTO_CLARO,
            "advertencia-texto": _ADVERTENCIA_TEXTO_CLARO,
        },
    },
    "gris": {
        "nombre": "Gris / Negro",
        "muestra": "#3a3f47",
        "oscura": True,
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
            "texto": _TEXTO_CLARO,
            "texto-tenue": _TEXTO_TENUE_CLARO,
            "fondo-1": "#1f2328",
            "fondo-2": "#0d0f12",
            "campo-fondo": "#0d0f12",
            "exito-texto": _EXITO_TEXTO_CLARO,
            "peligro-texto": _PELIGRO_TEXTO_CLARO,
            "advertencia-texto": _ADVERTENCIA_TEXTO_CLARO,
        },
    },
    "vino": {
        "nombre": "Vino / Rojo oscuro",
        "muestra": "#701f2e",
        "oscura": True,
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
            "texto": _TEXTO_CLARO,
            "texto-tenue": _TEXTO_TENUE_CLARO,
            "fondo-1": "#3a151b",
            "fondo-2": "#1f0a0d",
            "campo-fondo": "#1f0a0d",
            "exito-texto": _EXITO_TEXTO_CLARO,
            "peligro-texto": _PELIGRO_TEXTO_CLARO,
            "advertencia-texto": _ADVERTENCIA_TEXTO_CLARO,
        },
    },
    "blanco": {
        "nombre": "Blanco",
        "muestra": "#ffffff",
        "oscura": False,
        "variables": {
            # La barra superior y los íconos del menú se mantienen en azul
            # oscuro (como una franja de marca); el resto del sistema pasa
            # a fondo blanco con texto oscuro.
            "azul-950": "#0a1230",
            "azul-900": "#0f1a3d",
            "azul-800": "#14224f",
            "azul-700": "#1b2d68",
            "azul-600": "#24398a",
            "azul-500": "#3a52b4",
            "acento": "#3a66d6",
            "acento-2": "#2f5fd6",
            "superficie": "#ffffff",
            "superficie-2": "#f2f4f9",
            "borde": "#dde1ea",
            "texto": "#1a2340",
            "texto-tenue": "#5c657f",
            "fondo-1": "#ffffff",
            "fondo-2": "#eef1f7",
            "campo-fondo": "#ffffff",
            "exito-texto": "#0d7a4a",
            "peligro-texto": "#b3262b",
            "advertencia-texto": "#8a5a06",
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


def paleta_es_oscura(clave):
    """True si la paleta usa fondo oscuro / texto claro (todas menos
    'blanco'). Se usa para elegir la versión clara u oscura de los colores
    de las gráficas."""
    paleta = PALETAS.get(clave, PALETAS[PALETA_DEFECTO])
    return paleta.get("oscura", True)

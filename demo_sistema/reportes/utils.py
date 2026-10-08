"""Utilidades compartidas por los reportes: rango de fechas por defecto
(primer y último día del mes en curso), lectura de fechas desde la URL,
y el cálculo de los segmentos de la gráfica de pastel."""
import calendar
import math
from datetime import date, datetime

# Colores categóricos validados (paleta de referencia del método de
# accesibilidad de color): solo los 3 primeros de los 8 tonos pasan la
# verificación "todas contra todas" que necesita una gráfica de pastel
# (cada porción es vecina de todas las demás). Lo que sobra de esos 3 se
# agrupa en "Otros", con el gris de interfaz (invariante entre paletas
# claras y oscuras) en vez de inventar un cuarto tono.
COLOR_CATEGORICO_CLARO = ["#2a78d6", "#eb6834", "#1baf7a"]
COLOR_CATEGORICO_OSCURO = ["#3987e5", "#d95926", "#199e70"]
COLOR_OTROS = "#898781"

# Geometría del SVG del pastel: un <circle> con stroke-width = radio
# (así el "trazo" va del centro al borde, quedando como un disco relleno)
# y stroke-dasharray/offset por porción para recortar cada cuña.
RADIO_PASTEL = 80
CIRCUNFERENCIA_PASTEL = 2 * math.pi * (RADIO_PASTEL / 2)
_ESPACIO_PASTEL = 2.5  # separación visual entre porciones, en px de trazo


def rango_mes_actual():
    hoy = date.today()
    primer_dia = hoy.replace(day=1)
    ultimo_dia = hoy.replace(day=calendar.monthrange(hoy.year, hoy.month)[1])
    return primer_dia, ultimo_dia


def parsear_fecha(valor, por_defecto):
    if not valor:
        return por_defecto
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return por_defecto


def geometria_pastel():
    """Medidas del SVG del pastel, listas para usar en la plantilla sin
    hacer aritmética ahí: un <circle> con stroke-width = radio completo
    (el trazo va del centro al borde, quedando como un disco relleno).

    Todos los valores son enteros a propósito: con LANGUAGE_CODE="es" el
    motor de plantillas localiza los números al mostrarlos (usa coma en
    vez de punto decimal), lo cual rompería un atributo SVG como
    r="40,0". Un entero como 40 se muestra igual en cualquier idioma.
    """
    return {
        "r": RADIO_PASTEL // 2,
        "centro": RADIO_PASTEL,
        "viewbox": RADIO_PASTEL * 2,
        "trazo": RADIO_PASTEL,
    }


def calcular_pastel(filas, campo_etiqueta, campo_total, oscura, etiqueta_vacia):
    """Arma los segmentos de una gráfica de pastel a partir de filas ya
    agregadas (dicts con al menos campo_etiqueta y campo_total).

    Se muestran hasta 3 categorías (las de mayor total); el resto se agrupa
    en "Otros". La tabla del reporte sigue mostrando el detalle completo -
    la gráfica es un resumen visual, no la única fuente del dato.
    """
    colores = COLOR_CATEGORICO_OSCURO if oscura else COLOR_CATEGORICO_CLARO

    datos = []
    for f in filas:
        total = f.get(campo_total) or 0
        if total:
            etiqueta = f.get(campo_etiqueta) or etiqueta_vacia
            datos.append({"etiqueta": etiqueta, "total": total})

    datos.sort(key=lambda d: d["total"], reverse=True)
    principales, resto = datos[:3], datos[3:]

    segmentos = [
        {"etiqueta": d["etiqueta"], "total": d["total"], "color": colores[i]}
        for i, d in enumerate(principales)
    ]
    total_resto = sum(d["total"] for d in resto)
    if total_resto:
        segmentos.append({"etiqueta": "Otros", "total": total_resto, "color": COLOR_OTROS})

    total_general = sum(s["total"] for s in segmentos)
    if not total_general:
        return []

    acumulado = 0.0
    for s in segmentos:
        porcion = float(s["total"]) / float(total_general)
        largo = porcion * CIRCUNFERENCIA_PASTEL
        largo_visible = max(largo - _ESPACIO_PASTEL, 0)
        s["porcentaje"] = round(porcion * 100, 1)
        s["dasharray"] = f"{largo_visible:.2f} {max(CIRCUNFERENCIA_PASTEL - largo_visible, 0):.2f}"
        s["dashoffset"] = f"{-acumulado:.2f}"
        acumulado += largo

    return segmentos

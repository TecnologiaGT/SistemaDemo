"""Utilidades compartidas por los reportes: rango de fechas por defecto
(primer y último día del mes en curso) y lectura de fechas desde la URL."""
import calendar
from datetime import date, datetime


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

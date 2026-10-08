from openpyxl import Workbook
from openpyxl.styles import Font
from django.http import HttpResponse


def exportar_filas_excel(nombre_archivo, hoja, encabezados, filas):
    """Genera un HttpResponse con un archivo .xlsx a partir de encabezados y filas.

    nombre_archivo: nombre sugerido para la descarga (ej. "ventas.xlsx").
    hoja: nombre de la hoja dentro del libro (Excel limita a 31 caracteres).
    encabezados: lista de títulos de columna.
    filas: iterable de listas/tuplas con los valores de cada fila, en el
    mismo orden que los encabezados.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = hoja[:31]

    ws.append(list(encabezados))
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append(list(fila))

    for columna in ws.columns:
        largo_max = max((len(str(c.value)) for c in columna if c.value is not None), default=8)
        ws.column_dimensions[columna[0].column_letter].width = min(largo_max + 2, 45)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    wb.save(response)
    return response

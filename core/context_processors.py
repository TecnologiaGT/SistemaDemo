from .models import Personalizacion
from .paletas import variables_css


def personalizacion(request):
    """Pone la personalización (paleta + si hay foto de fondo) disponible
    en todas las plantillas, para que base.html pueda aplicar los colores."""
    config = Personalizacion.obtener()
    variables = variables_css(config.paleta)
    return {
        "personalizacion": config,
        "paleta_variables": variables,
        # Aparte del diccionario completo (para el bloque <style> con las
        # variables CSS), se expone este valor suelto porque las plantillas
        # de Django no pueden buscar una clave con guion (["azul-900"])
        # con la sintaxis de punto.
        "tema_color": variables.get("azul-900", "#0f1a3d"),
    }

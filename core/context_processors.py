from .models import Personalizacion
from .paletas import variables_css


def personalizacion(request):
    """Pone la personalización (paleta + si hay foto de fondo) disponible
    en todas las plantillas, para que base.html pueda aplicar los colores."""
    config = Personalizacion.obtener()
    return {
        "personalizacion": config,
        "paleta_variables": variables_css(config.paleta),
    }

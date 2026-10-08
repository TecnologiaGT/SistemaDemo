from decouple import config
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# Cuenta de mantenimiento del sistema: superusuario de Django que a
# propósito NO se vincula a ningún Empleado, así que nunca aparece en
# Empleados ni en ningún listado o selector de vendedores/administradores
# del sistema. Es la única cuenta que ve el cuadro "Reiniciar Sistema" en
# el panel principal (ver core.permissions.usuario_es_superusuario_oculto).
#
# La contraseña NO se escribe aquí en el código (este archivo se sube a
# GitHub): se lee de la variable de entorno USUARIO_MAESTRO_PASSWORD, igual
# que SECRET_KEY o DATABASE_URL. Hay que definirla en Render (pestaña
# Environment) para que este comando la use en cada despliegue.
USUARIO = "walde"


class Command(BaseCommand):
    help = "Crea (o actualiza la contraseña de) el superusuario de mantenimiento oculto."

    def handle(self, *args, **options):
        password = config("USUARIO_MAESTRO_PASSWORD", default="")
        if not password:
            self.stdout.write(self.style.WARNING(
                "No está definida la variable de entorno USUARIO_MAESTRO_PASSWORD; "
                "no se creó ni se modificó el usuario maestro."
            ))
            return

        user, creado = User.objects.get_or_create(
            username=USUARIO,
            defaults={"is_staff": True, "is_superuser": True},
        )
        if not creado:
            user.is_staff = True
            user.is_superuser = True
        user.set_password(password)
        user.save()

        if creado:
            self.stdout.write(self.style.SUCCESS(f"Usuario maestro '{USUARIO}' creado correctamente."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Usuario maestro '{USUARIO}' ya existía; contraseña actualizada."))

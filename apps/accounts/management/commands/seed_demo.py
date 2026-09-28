import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea usuarios de demostración con contraseñas aleatorias."

    def handle(self, *args, **options):
        user_model = get_user_model()
        demos = (
            ("cliente_demo", "cliente.demo@example.com", user_model.Role.CLIENT, "Camila"),
            ("prestador_demo", "prestador.demo@example.com", user_model.Role.PROVIDER, "Valentina"),
        )
        for username, email, role, first_name in demos:
            password = secrets.token_urlsafe(12)
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={"email": email, "role": role, "first_name": first_name},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
                self.stdout.write(self.style.SUCCESS(f"{username} creado; contraseña temporal: {password}"))
            else:
                self.stdout.write(f"{username} ya existe; no se cambió su contraseña.")

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Cliente"
        PROVIDER = "PROVIDER", "Prestador de servicios"
        ADMIN = "ADMIN", "Administrador"

    email = models.EmailField("correo electrónico", unique=True)
    role = models.CharField("rol", max_length=10, choices=Role.choices, default=Role.CLIENT)

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_provider(self):
        return self.role == self.Role.PROVIDER

    @property
    def is_platform_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    def __str__(self):
        return self.get_full_name() or self.username

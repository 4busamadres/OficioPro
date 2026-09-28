from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class RegistrationTests(TestCase):
    def test_provider_can_register_and_reaches_provider_dashboard(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "valentina",
                "first_name": "Valentina",
                "last_name": "Demo",
                "email": "valentina@example.com",
                "role": User.Role.PROVIDER,
                "password1": "Clave-Segura-2026",
                "password2": "Clave-Segura-2026",
            },
            follow=True,
        )
        self.assertContains(response, "Panel del prestador")
        self.assertEqual(User.objects.get(username="valentina").role, User.Role.PROVIDER)

    def test_public_cannot_open_dashboard(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}")

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(username="uno", email="persona@example.com", password="test-password")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "dos",
                "email": "PERSONA@example.com",
                "role": User.Role.CLIENT,
                "password1": "Clave-Segura-2026",
                "password2": "Clave-Segura-2026",
            },
        )
        self.assertContains(response, "Ya existe una cuenta con este correo.")
        self.assertEqual(User.objects.count(), 1)


class RoleDashboardTests(TestCase):
    def test_client_sees_only_client_dashboard(self):
        self.client.force_login(User.objects.create_user(username="cliente", email="cliente@example.com"))
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertContains(response, "Panel del cliente")
        self.assertNotContains(response, "Panel del prestador")

    def test_admin_role_is_sent_to_django_admin(self):
        user = User.objects.create_user(
            username="adminrol",
            email="adminrol@example.com",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, reverse("admin:index"), fetch_redirect_response=False)


class BookingPrototypeTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="reserva", email="reserva@example.com", role=User.Role.CLIENT
        )

    def test_catalog_is_public_and_shows_service_details(self):
        response = self.client.get(reverse("accounts:explore"))
        self.assertContains(response, "Manicura permanente")
        self.assertContains(response, "60 min")

    def test_client_can_create_and_cancel_demo_booking(self):
        self.client.force_login(self.client_user)
        response = self.client.post(
            reverse("accounts:book_service", args=["manicura-permanente"]),
            {"date": "2026-10-01", "time": "10:00"},
            follow=True,
        )
        self.assertContains(response, "Reserva confirmada")
        self.assertContains(response, "Confirmada")
        response = self.client.post(reverse("accounts:cancel_booking", args=[1]), follow=True)
        self.assertContains(response, "La reserva fue cancelada")
        self.assertContains(response, "Cancelada")

    def test_occupied_slot_cannot_be_reserved(self):
        self.client.force_login(self.client_user)
        response = self.client.post(
            reverse("accounts:book_service", args=["manicura-permanente"]),
            {"date": "2026-10-01", "time": "11:30"},
        )
        self.assertContains(response, "Selecciona un horario disponible")

    def test_provider_cannot_create_client_booking(self):
        provider = User.objects.create_user(
            username="profesional", email="profesional@example.com", role=User.Role.PROVIDER
        )
        self.client.force_login(provider)
        response = self.client.get(reverse("accounts:book_service", args=["manicura-permanente"]))
        self.assertEqual(response.status_code, 403)

    def test_client_can_save_and_remove_favorite(self):
        self.client.force_login(self.client_user)
        toggle_url = reverse("accounts:toggle_favorite", args=["manicura-permanente"])
        self.client.post(toggle_url)
        response = self.client.get(reverse("accounts:favorites"))
        self.assertContains(response, "Manicura permanente")
        self.client.post(toggle_url)
        response = self.client.get(reverse("accounts:favorites"))
        self.assertContains(response, "No has guardado servicios")

    def test_provider_can_accept_demo_request(self):
        provider = User.objects.create_user(
            username="agenda", email="agenda@example.com", role=User.Role.PROVIDER
        )
        self.client.force_login(provider)
        response = self.client.post(
            reverse("accounts:update_provider_request", args=[1, "accept"]), follow=True
        )
        self.assertContains(response, "ahora está confirmada")
        self.assertContains(response, "Confirmada")

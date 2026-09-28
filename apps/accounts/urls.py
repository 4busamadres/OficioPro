from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("registro/", views.register, name="register"),
    path(
        "ingresar/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("panel/", views.dashboard, name="dashboard"),
    path("explorar/", views.explore_services, name="explore"),
    path("servicio/<slug:service_slug>/", views.service_detail, name="service_detail"),
    path("servicio/<slug:service_slug>/reservar/", views.book_service, name="book_service"),
    path("reservas/", views.my_bookings, name="bookings"),
    path("reservas/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path("reservas/<int:booking_id>/cancelar/", views.cancel_booking, name="cancel_booking"),
    path("favoritos/", views.favorites, name="favorites"),
    path("favoritos/<slug:service_slug>/alternar/", views.toggle_favorite, name="toggle_favorite"),
    path("mis-servicios/", views.provider_services, name="provider_services"),
    path("agenda/", views.provider_schedule, name="provider_schedule"),
    path("solicitudes/", views.provider_requests, name="provider_requests"),
    path("solicitudes/<int:request_id>/<str:action>/", views.update_provider_request, name="update_provider_request"),
    path("perfil/", views.profile, name="profile"),
    path("notificaciones/", views.notifications, name="notifications"),
    path("ayuda/", views.help_center, name="help"),
]

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from .forms import RegistrationForm
from .models import User


DEMO_SERVICES = [
    {
        "slug": "manicura-permanente",
        "name": "Manicura permanente",
        "provider": "Camila Soto",
        "price": 18000,
        "duration": 60,
        "location": "Providencia, Santiago",
        "description": "Limpieza, preparación de uñas, esmaltado permanente y acabado hidratante.",
        "initials": "CS",
    },
    {
        "slug": "soft-gel",
        "name": "Extensión Soft Gel",
        "provider": "Valentina Rojas",
        "price": 25000,
        "duration": 90,
        "location": "Ñuñoa, Santiago",
        "description": "Extensión de uñas con sistema Soft Gel, color a elección y terminación profesional.",
        "initials": "VR",
    },
    {
        "slug": "nail-art",
        "name": "Manicura con Nail Art",
        "provider": "Daniela Muñoz",
        "price": 22000,
        "duration": 75,
        "location": "La Florida, Santiago",
        "description": "Manicura completa con diseño personalizado sencillo en hasta cuatro uñas.",
        "initials": "DM",
    },
]

DEMO_DATES = [
    ("2026-10-01", "Jue 1 oct"),
    ("2026-10-02", "Vie 2 oct"),
    ("2026-10-03", "Sáb 3 oct"),
]
DEMO_SLOTS = [
    ("10:00", "available", "Disponible"),
    ("11:30", "occupied", "Ocupado"),
    ("13:00", "available", "Disponible"),
    ("15:30", "available", "Disponible"),
    ("17:00", "occupied", "Ocupado"),
]

DEMO_PROVIDER_REQUESTS = [
    {"id": 1, "client": "Fernanda Pérez", "service": "Manicura permanente", "date": "2026-10-01", "time": "10:00", "price": 18000, "status": "Pendiente"},
    {"id": 2, "client": "Javiera Silva", "service": "Extensión Soft Gel", "date": "2026-10-02", "time": "15:30", "price": 25000, "status": "Confirmada"},
    {"id": 3, "client": "Antonia Díaz", "service": "Manicura con Nail Art", "date": "2026-10-03", "time": "13:00", "price": 22000, "status": "Completada"},
]


def _service_or_404(slug):
    from django.http import Http404
    service = next((item for item in DEMO_SERVICES if item["slug"] == slug), None)
    if not service:
        raise Http404("Servicio no encontrado")
    return service


def _require_role(request, role):
    if request.user.role != role:
        raise PermissionDenied


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Tu cuenta fue creada correctamente. Ya puedes usar tu panel.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.is_platform_admin:
        return redirect("admin:index")
    if request.user.role == User.Role.PROVIDER:
        return render(request, "accounts/provider_dashboard.html")
    if request.user.role == User.Role.CLIENT:
        return render(request, "accounts/client_dashboard.html")
    raise PermissionDenied


def explore_services(request):
    return render(request, "accounts/explore.html", {"services": DEMO_SERVICES, "favorite_slugs": request.session.get("demo_favorites", [])})


def service_detail(request, service_slug):
    return render(request, "accounts/service_detail.html", {"service": _service_or_404(service_slug), "favorite_slugs": request.session.get("demo_favorites", [])})


@login_required
def book_service(request, service_slug):
    _require_role(request, User.Role.CLIENT)
    service = _service_or_404(service_slug)
    selected_date = request.POST.get("date", request.GET.get("date", ""))
    selected_time = request.POST.get("time", request.GET.get("time", ""))
    valid_dates = {value for value, _ in DEMO_DATES}
    valid_times = {value for value, state, _ in DEMO_SLOTS if state == "available"}
    errors = []
    if request.method == "POST":
        if selected_date not in valid_dates:
            errors.append("Selecciona una fecha disponible.")
        if selected_time not in valid_times:
            errors.append("Selecciona un horario disponible.")
        if not errors:
            bookings = request.session.get("demo_bookings", [])
            booking = {
                "id": max([item["id"] for item in bookings], default=0) + 1,
                "service": service["name"], "provider": service["provider"],
                "price": service["price"], "duration": service["duration"],
                "date": selected_date, "time": selected_time, "status": "Confirmada",
            }
            bookings.append(booking)
            request.session["demo_bookings"] = bookings
            messages.success(request, "Reserva confirmada. Puedes revisar el detalle en Mis reservas.")
            return redirect("accounts:bookings")
    return render(request, "accounts/book_service.html", {
        "service": service, "dates": DEMO_DATES, "slots": DEMO_SLOTS,
        "selected_date": selected_date, "selected_time": selected_time, "errors": errors,
    })


@login_required
def my_bookings(request):
    _require_role(request, User.Role.CLIENT)
    return render(request, "accounts/bookings.html", {"bookings": request.session.get("demo_bookings", [])})


@login_required
def booking_detail(request, booking_id):
    from django.http import Http404
    _require_role(request, User.Role.CLIENT)
    booking = next((item for item in request.session.get("demo_bookings", []) if item["id"] == booking_id), None)
    if not booking:
        raise Http404("Reserva no encontrada")
    return render(request, "accounts/booking_detail.html", {"booking": booking})


@login_required
def cancel_booking(request, booking_id):
    _require_role(request, User.Role.CLIENT)
    if request.method != "POST":
        return redirect("accounts:bookings")
    bookings = request.session.get("demo_bookings", [])
    found = False
    for booking in bookings:
        if booking["id"] == booking_id and booking["status"] == "Confirmada":
            booking["status"] = "Cancelada"
            found = True
    request.session["demo_bookings"] = bookings
    if found:
        messages.success(request, "La reserva fue cancelada correctamente.")
    else:
        messages.error(request, "No fue posible cancelar esa reserva.")
    return redirect("accounts:bookings")


@login_required
def favorites(request):
    _require_role(request, User.Role.CLIENT)
    favorite_slugs = request.session.get("demo_favorites", [])
    services = [item for item in DEMO_SERVICES if item["slug"] in favorite_slugs]
    return render(request, "accounts/favorites.html", {"services": services})


@login_required
def toggle_favorite(request, service_slug):
    _require_role(request, User.Role.CLIENT)
    service = _service_or_404(service_slug)
    if request.method != "POST":
        return redirect("accounts:service_detail", service_slug=service_slug)
    favorite_slugs = request.session.get("demo_favorites", [])
    if service_slug in favorite_slugs:
        favorite_slugs.remove(service_slug)
        messages.success(request, f"Quitaste {service['name']} de tus favoritos.")
    else:
        favorite_slugs.append(service_slug)
        messages.success(request, f"Guardaste {service['name']} en tus favoritos.")
    request.session["demo_favorites"] = favorite_slugs
    return redirect(request.POST.get("next") or "accounts:favorites")


@login_required
def provider_services(request):
    _require_role(request, User.Role.PROVIDER)
    return render(request, "accounts/provider_services.html", {"services": DEMO_SERVICES[:2]})


@login_required
def provider_schedule(request):
    _require_role(request, User.Role.PROVIDER)
    return render(request, "accounts/provider_schedule.html", {"dates": DEMO_DATES, "slots": DEMO_SLOTS})


@login_required
def provider_requests(request):
    _require_role(request, User.Role.PROVIDER)
    requests_data = request.session.get("demo_provider_requests", DEMO_PROVIDER_REQUESTS)
    return render(request, "accounts/provider_requests.html", {"requests_data": requests_data})


@login_required
def update_provider_request(request, request_id, action):
    _require_role(request, User.Role.PROVIDER)
    if request.method != "POST" or action not in {"accept", "reject", "complete"}:
        return redirect("accounts:provider_requests")
    requests_data = request.session.get("demo_provider_requests", [dict(item) for item in DEMO_PROVIDER_REQUESTS])
    item = next((entry for entry in requests_data if entry["id"] == request_id), None)
    transitions = {"accept": "Confirmada", "reject": "Rechazada", "complete": "Completada"}
    if item:
        item["status"] = transitions[action]
        request.session["demo_provider_requests"] = requests_data
        messages.success(request, f"La solicitud de {item['client']} ahora está {item['status'].lower()}.")
    return redirect("accounts:provider_requests")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def notifications(request):
    return render(request, "accounts/notifications.html")


def help_center(request):
    return render(request, "accounts/help.html")

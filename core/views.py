import math
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import RegisterForm, ZoneForm
from .models import EntryLog, Zone


def staff_required(view_func):
    """Like staff_member_required, but bounces non-staff back into the app
    with our own themed pages instead of Django's built-in admin login."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        if not request.user.is_staff:
            messages.error(request, "That area is for admin accounts only.")
            return redirect("user_dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped


def haversine_m(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points, in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(min(1, math.sqrt(a)))


# ---------------------------------------------------------------- public --

def landing(request):
    if request.user.is_authenticated:
        return redirect("post_login_redirect")
    return render(request, "landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("post_login_redirect")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("post_login_redirect")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


@login_required
def post_login_redirect(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")
    return redirect("user_dashboard")


# ------------------------------------------------------------- user side --

@login_required
def user_dashboard(request):
    zones = Zone.objects.filter(is_active=True)
    my_recent = EntryLog.objects.filter(user=request.user).select_related("zone")[:8]
    zones_json = [
        {"id": z.id, "name": z.name, "lat": z.center_lat, "lng": z.center_lng,
         "radius_m": z.radius_m, "color": z.color}
        for z in zones
    ]
    return render(
        request,
        "user_dashboard.html",
        {
            "zones": zones,
            "zones_json": zones_json,
            "my_recent": my_recent,
            "cooldown": settings.CHECKIN_COOLDOWN_MINUTES,
        },
    )


@login_required
@require_POST
def api_checkin(request):
    """
    Receives {lat, lng} from the browser's geolocation watcher.
    Re-validates server-side against every active zone and records an
    EntryLog for any zone the point currently falls inside, respecting
    the cooldown so a stationary user doesn't spam the table.
    """
    try:
        lat = float(request.POST.get("lat"))
        lng = float(request.POST.get("lng"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid coordinates."}, status=400)

    cooldown = timedelta(minutes=settings.CHECKIN_COOLDOWN_MINUTES)
    cutoff = timezone.now() - cooldown

    entered_zones = []
    skipped_zones = []
    for zone in Zone.objects.filter(is_active=True):
        distance = haversine_m(lat, lng, zone.center_lat, zone.center_lng)
        if distance <= zone.radius_m:
            recent = EntryLog.objects.filter(
                user=request.user, zone=zone, entered_at__gte=cutoff
            ).exists()
            if recent:
                skipped_zones.append(zone.name)
                continue
            EntryLog.objects.create(user=request.user, zone=zone, lat=lat, lng=lng)
            entered_zones.append(zone.name)

    return JsonResponse(
        {
            "ok": True,
            "entered": entered_zones,
            "already_logged": skipped_zones,
            "checked_at": timezone.now().isoformat(),
        }
    )


# ------------------------------------------------------------ admin side --

@staff_required
def admin_dashboard(request):
    zones = Zone.objects.all()
    entries = EntryLog.objects.select_related("user", "zone")[:100]
    return render(request, "admin_dashboard.html", {"zones": zones, "entries": entries})


@staff_required
def api_recent_entries(request):
    """JSON feed the admin dashboard polls every few seconds."""
    entries = EntryLog.objects.select_related("user", "zone")[:100]
    data = [
        {
            "id": e.id,
            "username": e.user.username,
            "zone": e.zone.name,
            "lat": e.lat,
            "lng": e.lng,
            "entered_at": timezone.localtime(e.entered_at).strftime("%d %b %Y, %H:%M:%S"),
        }
        for e in entries
    ]
    return JsonResponse({"entries": data, "count": EntryLog.objects.count()})


@staff_required
def zone_list(request):
    zones = Zone.objects.all()
    return render(request, "zone_list.html", {"zones": zones})


@staff_required
def zone_create(request):
    if request.method == "POST":
        form = ZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.created_by = request.user
            zone.save()
            return redirect("zone_list")
    else:
        form = ZoneForm()
    return render(request, "zone_form.html", {"form": form, "mode": "create"})


@staff_required
def zone_edit(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    if request.method == "POST":
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            form.save()
            return redirect("zone_list")
    else:
        form = ZoneForm(instance=zone)
    return render(request, "zone_form.html", {"form": form, "mode": "edit", "zone": zone})


@staff_required
@require_POST
def zone_delete(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    zone.delete()
    return redirect("zone_list")


# ----------------------------------------------------------------- shared --

@login_required
def api_zones(request):
    """Active zones as JSON, used to draw circles on either map."""
    zones = Zone.objects.filter(is_active=True)
    data = [
        {
            "id": z.id,
            "name": z.name,
            "lat": z.center_lat,
            "lng": z.center_lng,
            "radius_m": z.radius_m,
            "color": z.color,
        }
        for z in zones
    ]
    return JsonResponse({"zones": data})

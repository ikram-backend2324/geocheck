from django.conf import settings
from django.db import models
from django.utils import timezone


class Zone(models.Model):
    """A circular geofenced area: a center point plus a radius in meters."""

    name = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    center_lat = models.FloatField()
    center_lng = models.FloatField()
    radius_m = models.PositiveIntegerField(default=150, help_text="Radius in meters")
    color = models.CharField(max_length=7, default="#4cf0b0", help_text="Hex color for the map")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EntryLog(models.Model):
    """One record of a user's GPS coordinates falling inside a Zone."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="entries"
    )
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="entries")
    lat = models.FloatField()
    lng = models.FloatField()
    entered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-entered_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.zone.name} @ {self.entered_at:%Y-%m-%d %H:%M}"

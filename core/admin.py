from django.contrib import admin

from .models import EntryLog, Zone


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "radius_m", "is_active", "created_by", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(EntryLog)
class EntryLogAdmin(admin.ModelAdmin):
    list_display = ("user", "zone", "entered_at", "lat", "lng")
    list_filter = ("zone",)
    search_fields = ("user__username",)
    date_hierarchy = "entered_at"

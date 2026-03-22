from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "room_type",
        "check_in",
        "check_out",
        "guests",
        "status",
        "created_at",
    )
    list_filter = ("status", "check_in", "check_out", "created_at")
    search_fields = (
        "full_name",
        "email",
        "phone",
        "room_type__name",
        "room_type__hotel__name",
    )
    autocomplete_fields = ("room_type", "user")
    date_hierarchy = "created_at"



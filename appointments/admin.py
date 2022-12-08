from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Booking


class BookingAdmin(SimpleHistoryAdmin):
    autocomplete_fields = ("booked_property",)
    search_fields = ["booking_date",
                     "booking_time"]


admin.site.register(Booking, BookingAdmin)

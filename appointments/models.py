import datetime

import pytz
# https://pypi.org/project/backports.zoneinfo/
from backports.zoneinfo import ZoneInfo
from django.db import models
from django.utils import timezone
from model_utils import FieldTracker
from simple_history.models import HistoricalRecords
from timezonefinder import TimezoneFinder
from core.models import CommonInfo
from phonenumber_field.modelfields import PhoneNumberField

from .constants import OPTIONAL

tzf = TimezoneFinder()


class Booking(models.Model):
    """
    Holds all the booking information on the property
    """

    # Bookings track when appointments are booked, it will be called appointment on the present day of the booking date
    booked_property = models.ForeignKey(
        "crea_parser.Property", on_delete=models.CASCADE, related_name="booked_property"
    )
    agents = models.ManyToManyField(
        'users.User', blank=True, related_name="booking_agent_set"
    )
    approved_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="approved_by", **OPTIONAL
    )
    booking_date = models.DateField(auto_now_add=False, **OPTIONAL)
    booking_time = models.TimeField(auto_now=False, **OPTIONAL)
    date_canceled = models.DateField(auto_now=False, **OPTIONAL)
    cancel_reason = models.TextField(**OPTIONAL)
    date_created = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return str('{} {}'.format(self.booked_property, self.booking_date))

    @property
    def property_tz(self):
        # Longtitude and Latitude
        try:
            longitude = float(self.booked_property.Geo.lng)
            latitude = float(self.booked_property.Geo.lat)
            # Get timezone of the property from longitude/latitude value
            property_tz = tzf.timezone_at(lng=longitude, lat=latitude)

            return property_tz
        except:
            # Returns none when querying the Geolocation encounter an error
            return None

    def save(self, *args, **kwargs):
        if (
            self._state.adding
            or self.tracker.has_changed("booking_date")
            or self.tracker.has_changed("booking_time")
        ):

            date, time = self.convert_datetime_to_property_tz()
            self.booking_date = date
            self.booking_time = time

        super(Booking, self).save(*args, **kwargs)

    def convert_datetime_to_property_tz(self, *args, **kwargs):
        # Get timezone of the property from longitude/latitude value
        ptz = self.property_tz
        # Tokenize date and time
        date, month, year, hour, minute = (
            self.booking_date.day,
            self.booking_date.month,
            self.booking_date.year,
            self.booking_time.hour,
            self.booking_time.minute,
        )
        # Create naive datetime object
        naive = datetime.datetime(year, month, date, hour, minute)

        if ptz:
            # Make date property timezone aware
            property_tz_aware = timezone.make_aware(naive, timezone=pytz.timezone(ptz))
        else:
            # If no timezone. Set default to Edmonton
            property_tz_aware = timezone.make_aware(
                naive, timezone=pytz.timezone("America/Edmonton")
            )
        # Make utc aware for saving ready and return
        utc = property_tz_aware.astimezone(pytz.utc)

        return utc.date(), utc.time()


class BookingClient(CommonInfo):
    """
        Booking client's allowing us to assign multiple clients to a specific booking.
    """

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_client", null=True
    )

    first_name = models.CharField(max_length=225, null=True, blank=True)
    last_name = models.CharField(max_length=225, null=True, blank=True)
    email = models.EmailField(max_length=225, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name="buyer_user", null=True
    )

    def __str__(self):
        return f"{self.booking} by {self.user}"
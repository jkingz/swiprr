from django import dispatch
from django.db.models.signals import post_save, pre_save
from django.db import transaction
from django.dispatch import receiver

from .utils import (
    _send_client_notification,
    _send_agent_notification,
    _send_admin_notification,
)

from .constants import (
    EmailType,
    ClientMessages,
    AgentMessages,
    AdminMessages
)


class AppointmentSignal(object):
    """
    Signal for Bookings / Booking Client to trigger send email notification on each successful database transaction.
    """

    @receiver(post_save, sender="appointments.Booking", dispatch_uid="appointments.models.Booking")
    def trigger_booking_email_notification(sender, instance, created, **kwargs):
        if created:

            _send_admin_notification(instance, EmailType.NEW_BOOKING, AdminMessages.NEW_BOOKING_MESSAGE)

        else:
            tracker = instance.tracker

            # For booking reschedule
            # We first check if the field has changed,
            # then check if the previous value is not the same with the new value.

            if (tracker.has_changed('booking_date') and tracker.previous('booking_date') != instance.booking_date) or \
                    (tracker.has_changed('booking_time') and tracker.previous('booking_time') != instance.booking_time):
                _send_client_notification(instance, EmailType.RESCHEDULED_BOOKING,
                                          ClientMessages.RESCHEDULED_BOOKING_MESSAGE + str(instance.booking_date) +
                                          ' ' + str(instance.booking_time))
                _send_agent_notification(instance, EmailType.RESCHEDULED_BOOKING,
                                         AgentMessages.RESCHEDULED_BOOKING_MESSAGE + str(instance.booking_date) +
                                         ' ' + str(instance.booking_time))
                _send_admin_notification(instance, EmailType.RESCHEDULED_BOOKING,
                                         AdminMessages.RESCHEDULED_BOOKING_MESSAGE + str(instance.booking_date) +
                                         ' ' + str(instance.booking_time))

            if (tracker.has_changed('is_approved') and tracker.previous('is_approved') != instance.is_approved and
                    instance.is_approved is True) and (instance.date_canceled is None):
                _send_client_notification(instance, EmailType.CONFIRMED_BOOKING,
                                          ClientMessages.CONFIRMED_BOOKING_MESSAGE)
                _send_agent_notification(instance, EmailType.CONFIRMED_BOOKING,
                                         AgentMessages.CONFIRMED_BOOKING_MESSAGE)
                _send_admin_notification(instance, EmailType.CONFIRMED_BOOKING,
                                         AdminMessages.CONFIRMED_BOOKING_MESSAGE)

            if (tracker.has_changed('date_canceled') and tracker.previous('date_canceled') != instance.date_canceled) \
                    and (instance.date_canceled is not None):
                _send_client_notification(instance, EmailType.CANCELED_BOOKING,
                                          ClientMessages.CANCELED_BOOKING_MESSAGE)
                _send_agent_notification(instance, EmailType.CANCELED_BOOKING,
                                         AgentMessages.CANCELED_BOOKING_MESSAGE)
                _send_admin_notification(instance, EmailType.CANCELED_BOOKING,
                                         AdminMessages.CANCELED_BOOKING_MESSAGE)

    @receiver(pre_save, sender="appointments.BookingClient", dispatch_uid="appointments.models.BookingClient")
    def trigger_booking_client_email_notification(sender, instance, **kwargs):
        booking = instance.booking
        client_count = booking.booking_client.all().count()

        if client_count == 0:
            _send_client_notification(instance, EmailType.NEW_BOOKING, ClientMessages.NEW_BOOKING_MESSAGE)

        if client_count > 0:
            _send_client_notification(instance, EmailType.CLIENT_ASSIGNMENT,
                                      ClientMessages.CLIENT_ASSIGNMENT_MESSAGE)
            _send_agent_notification(instance, EmailType.CLIENT_ASSIGNMENT,
                                     AgentMessages.CLIENT_ASSIGNMENT_MESSAGE)
            _send_admin_notification(instance, EmailType.CLIENT_ASSIGNMENT,
                                     AdminMessages.CLIENT_ASSIGNMENT_MESSAGE)

# from django.contrib.sites.models import Site
from decouple import config


class Config(object):
    FRONT_END_PROPERTY_URL = "https://sample.com/property"
    # ROOT_URL = Site.objects.get_current().domain
    ADMIN_EMAIL = config("SHOWINGS_EMAIL", default="")
    EMAIL_SUBJECT = "Booking Notification!"


class EmailType(object):
    NEW_BOOKING = 'new_booking'
    CONFIRMED_BOOKING = 'confirmed_booking'
    CANCELED_BOOKING = 'canceled_booking'
    RESCHEDULED_BOOKING = 'rescheduled_booking'
    UNLOCKED_BOOKING = 'unlocked_booking'
    CLIENT_ASSIGNMENT = 'client_assignment'
    AGENT_ASSIGNMENT = 'agent_assignment'


class ClientMessages(object):
    HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE = "booking/email/client/email_booking_notification.txt"
    TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE = "booking/email/client/email_booking_notification.html"

    NEW_BOOKING_MESSAGE = 'has been successfully requested'
    CONFIRMED_BOOKING_MESSAGE = 'has been confirmed'
    CANCELED_BOOKING_MESSAGE = 'has been canceled'
    RESCHEDULED_BOOKING_MESSAGE = 'has been rescheduled to '
    CLIENT_ASSIGNMENT_MESSAGE = 'You have been added to a booking for '
    UNLOCKED_BOOKING_MESSAGE = 'has been successfully reconsider and ready to be amended ' \
                               'for a new schedule on property'


class AgentMessages(object):
    HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE = "booking/email/agent/email_booking_notification.txt"
    TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE = "booking/email/agent/email_booking_notification.html"

    CONFIRMED_BOOKING_MESSAGE = 'has been confirmed'
    CANCELED_BOOKING_MESSAGE = 'has been canceled'
    RESCHEDULED_BOOKING_MESSAGE = 'has been rescheduled to '
    CLIENT_ASSIGNMENT_MESSAGE = 'A new client has been added to a booking for '
    AGENT_ASSIGNMENT_ALL_MESSAGE = 'A new agent has been added to a booking for '
    AGENT_ASSIGNMENT_SELF_MESSAGE = 'You have been added to a booking for '


class AdminMessages(object):
    HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE = "booking/email/admin/email_booking_notification.txt"
    TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE = "booking/email/admin/email_booking_notification.html"

    NEW_BOOKING_MESSAGE = 'has been successfully requested'
    CONFIRMED_BOOKING_MESSAGE = 'has been confirmed'
    CANCELED_BOOKING_MESSAGE = 'has been canceled'
    RESCHEDULED_BOOKING_MESSAGE = 'has been rescheduled to '
    CLIENT_ASSIGNMENT_MESSAGE = 'A new client has been added to a booking for '
    AGENT_ASSIGNMENT_MESSAGE = 'A new agent has been added to a booking for '


OPTIONAL = {"blank": True, "null": True}

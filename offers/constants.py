from django.contrib.sites.models import Site
from decouple import config

OPTIONAL = {"blank": True, "null": True}


class Config(object):
    ROOT_URL = Site.objects.get_current().domain
    FRONT_END_OFFER_URL = "https://frontend.com/requestOfferDocs"
    ADMIN_EMAIL = config("SUPPORT_EMAIL", default="")
    EMAIL_SUBJECT = "Offer Notification!"


class EmailType(object):
    NEW_OFFER = 'new_offer'
    UPDATE_OFFER = 'update_offer'
    UPDATE_OFFER_STATUS = 'update_offer_status'
    AGENT_ASSIGNMENT = 'agent_assignment'
    OFFER_STEPS = 'offer_steps'


class AdminMessages(object):
    HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE = "offer/email/admin/email_offer_notification.txt"
    TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE = "offer/email/admin/email_offer_notification.html"

    NEW_OFFER_MESSAGE = 'A new offer has been successfully created'
    UPDATE_OFFER_MESSAGE = 'An offer has been successfully updated'
    UPDATE_OFFER_STATUS_MESSAGE = 'The offer status has been successfully updated to '
    AGENT_ASSIGNMENT_MESSAGE = 'A new agent has been added to a offer'


class AgentMessages(object):
    HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE = "offer/email/agent/email_offer_notification.txt"
    TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE = "offer/email/agent/email_offer_notification.html"

    NEW_OFFER_MESSAGE = 'A new offer has been created'
    UPDATE_OFFER_MESSAGE = 'An offer has been updated'
    UPDATE_OFFER_STATUS_MESSAGE = 'The offer status has been updated to '
    AGENT_ASSIGNMENT_ALL_MESSAGE = 'A new agent has been added to a offer'
    AGENT_ASSIGNMENT_SELF_MESSAGE = 'You have been added to a offer'


class StepsMessages(object):
    HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE = "offer/email/steps/email_offer_notification.txt"
    TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE = "offer/email/steps/email_offer_notification.html"

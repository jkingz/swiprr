# from django.contrib.sites.models import Site
from decouple import config

OPTIONAL = {
    'blank': True,
    'null': True
}


class Config(object):
    FRONT_END_DEAL_URL = "https://frontend.com/dealsNew"
    # ROOT_URL = Site.objects.get_current().domain
    ADMIN_EMAIL = config("SUPPORT_EMAIL", default="")
    EMAIL_SUBJECT = "Deal Notification!"


class EmailType(object):
    NEW_DEAL = 'new_deal'
    UPDATE_DEAL = 'update_deal'
    UPDATE_DEAL_STATUS = 'update_deal_status'
    AGENT_ASSIGNMENT = 'agent_assignment'


class AdminMessages(object):
    HTML_DEAL_NOTIFICATION_EMAIL_TEMPLATE = "deal/email/admin/email_deal_notification.txt"
    TEXT_DEAL_NOTIFICATION_EMAIL_TEMPLATE = "deal/email/admin/email_deal_notification.html"

    NEW_DEAL_MESSAGE = 'A new deal has been successfully created'
    UPDATE_DEAL_MESSAGE = 'A deal has been successfully updated'
    UPDATE_DEAL_STATUS_MESSAGE = 'The deal status has been successfully updated to '
    AGENT_ASSIGNMENT_MESSAGE = 'A new agent has been added to a deal'


class AgentMessages(object):
    HTML_DEAL_NOTIFICATION_EMAIL_TEMPLATE = "deal/email/agent/email_deal_notification.txt"
    TEXT_DEAL_NOTIFICATION_EMAIL_TEMPLATE = "deal/email/agent/email_deal_notification.html"

    NEW_DEAL_MESSAGE = 'Deal has been successfully created'
    UPDATE_DEAL_MESSAGE = 'A deal has been updated'
    UPDATE_DEAL_STATUS_MESSAGE = 'The deal status has been updated to '
    AGENT_ASSIGNMENT_ALL_MESSAGE = 'A new agent has been added to a deal'
    AGENT_ASSIGNMENT_SELF_MESSAGE = 'You have been added to a deal'

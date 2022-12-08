from django.contrib.sites.models import Site
from decouple import config


class Config(object):
    FRONT_END_LEAD_URL = "https://frontend.com/contact_lead"
    ROOT_URL = Site.objects.get_current().domain
    ADMIN_EMAIL = config("SHOWINGS_EMAIL", default="")
    EMAIL_SUBJECT = "Lead Notification!"


class EmailType(object):
    NEW_LEAD = 'new_lead'
    AGENT_ASSIGNMENT = 'agent_assignment'
    MORTGAGE_ASSIGNMENT = 'mortgage_assignment'
    SALES_AGENT_ASSIGNMENT = 'sales_agent_assignment'
    AGENT_UNASSIGNED = 'agent_unassigned'
    MORTGAGE_UNASSIGNED = 'mortgage_unassigned'
    SALES_AGENT_UNASSIGNED = 'sales_agent_unassigned'


class AdminMessages(object):
    HTML_LEAD_NOTIFICATION_EMAIL_TEMPLATE = "lead/email/admin/email_lead_notification.txt"
    TEXT_LEAD_NOTIFICATION_EMAIL_TEMPLATE = "lead/email/admin/email_lead_notification.html"

    NEW_LEAD_MESSAGE = 'A new lead has been successfully created'
    AGENT_ASSIGNMENT_MESSAGE = 'A new agent has been added to a lead'
    MORTGAGE_ASSIGNMENT_MESSAGE = 'A new mortgage broker has been added to a lead'
    SALES_AGENT_ASSIGNMENT_MESSAGE = 'A new sales agent has been added to a lead'
    AGENT_UNASSIGNED_MESSAGE = 'A agent has been removed to a lead'
    MORTGAGE_UNASSIGNED_MESSAGE = 'A mortgage broker has been removed to a lead'
    SALES_AGENT_UNASSIGNED_MESSAGE = 'A sales agent has been removed to a lead'


class AgentMessages(object):
    HTML_LEAD_NOTIFICATION_EMAIL_TEMPLATE = "lead/email/agent/email_lead_notification.txt"
    TEXT_LEAD_NOTIFICATION_EMAIL_TEMPLATE = "lead/email/agent/email_lead_notification.html"

    NEW_LEAD_MESSAGE = 'Lead has been successfully created'
    AGENT_ASSIGNMENT_ALL_MESSAGE = 'A new agent has been added to a lead'
    AGENT_ASSIGNMENT_SELF_MESSAGE = 'You have been added to a lead'
    MORTGAGE_ASSIGNMENT_ALL_MESSAGE = 'A new mortgage broker has been added to a lead'
    MORTGAGE_ASSIGNMENT_SELF_MESSAGE = 'You have been added to a lead'
    SALES_AGENT_ASSIGNMENT_ALL_MESSAGE = 'A new sales agent has been added to a lead'
    SALES_AGENT_ASSIGNMENT_SELF_MESSAGE = 'You have been added to a lead'
    AGENT_UNASSIGNED_MESSAGE = 'You have been removed to a lead'
    MORTGAGE_UNASSIGNED_MESSAGE = 'You have been removed to a lead'
    SALES_AGENT_UNASSIGNED_MESSAGE = 'You have been removed to a lead'

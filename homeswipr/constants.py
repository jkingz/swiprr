from django.contrib.sites.models import Site
from decouple import config


class Config(object):
    FRONT_END_SAVED_SEARCH_URL = "https://frontend.com/savedsearches"
    ROOT_URL = Site.objects.get_current().domain
    ADMIN_EMAIL = config("SHOWINGS_EMAIL", default="")
    EMAIL_SUBJECT = "Saved Search Notification!"


class EmailType(object):
    NEW_SAVED_SEARCH = 'new_saved_search'
    UPDATED_TITLE_SAVED_SEARCH = 'updated_title_saved_search'
    UPDATED_FREQUENCY_SAVED_SEARCH = 'updated_frequency_saved_search'
    DELETED_SAVED_SEARCH = 'deleted_saved_search'
    AGENT_ASSIGNMENT = 'agent_assignment'


class ClientMessages(object):
    HTML_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE = "saved_search/email/client/email_saved_search_notification.txt"
    TEXT_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE = "saved_search/email/client/email_saved_search_notification.html"

    NEW_SAVED_SEARCH_MESSAGE = 'has been successfully created'
    UPDATED_TITLE_MESSAGE = 'has been renamed to '
    UPDATED_FREQUENCY_MESSAGE = 'has been updated to '
    DELETED_SAVED_SEARCH_MESSAGE = 'has been deleted'


class AgentMessages(object):
    HTML_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE = "saved_search/email/agent/email_saved_search_notification.txt"
    TEXT_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE = "saved_search/email/agent/email_saved_search_notification.html"

    UPDATED_TITLE_MESSAGE = 'has been renamed to '
    UPDATED_FREQUENCY_MESSAGE = 'has been updated to '
    DELETED_SAVED_SEARCH_MESSAGE = 'has been deleted'
    AGENT_ASSIGNMENT_SELF_MESSAGE = 'You have been added to the saved search '
    AGENT_ASSIGNMENT_ALL_MESSAGE = 'A new agent has been added to the saved search '


class AdminMessages(object):
    HTML_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE = "saved_search/email/admin/email_saved_search_notification.txt"
    TEXT_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE = "saved_search/email/admin/email_saved_search_notification.html"

    NEW_SAVED_SEARCH_MESSAGE = 'has been successfully created'
    UPDATED_TITLE_MESSAGE = 'has been renamed to '
    UPDATED_FREQUENCY_MESSAGE = 'has been updated to '
    DELETED_SAVED_SEARCH_MESSAGE = 'has been deleted'
    AGENT_ASSIGNMENT_MESSAGE = 'A new agent has been added to the saved search '

from django.contrib.sites.models import Site
from decouple import config

OPTIONAL = {
    'blank': True,
    'null': True
}


class Config(object):
    FRONT_END_USER_URL = "https://frontend.com/"
    ROOT_URL = Site.objects.get_current().domain
    ADMIN_EMAIL = config("SUPPORT_EMAIL", default="")
    EMAIL_SUBJECT = "Referral Notification!"


class EmailType(object):
    REFERRAL = 'referral'


class AgentMessages(object):
    HTML_USER_NOTIFICATION_EMAIL_TEMPLATE = "user/email/agent/email_user_notification.txt"
    TEXT_USER_NOTIFICATION_EMAIL_TEMPLATE = "user/email/agent/email_user_notification.html"

    REFERRAL_MESSAGE = 'A user has been successfully registered with your referral code'


class ClientMessages(object):
    HTML_USER_NOTIFICATION_EMAIL_TEMPLATE = "user/email/client/email_user_notification.txt"
    TEXT_USER_NOTIFICATION_EMAIL_TEMPLATE = "user/email/client/email_user_notification.html"

    REFERRAL_MESSAGE = 'You have been successfully registered with a referral code from '

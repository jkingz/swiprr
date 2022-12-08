from core.utils import HomeswiprMailer
from .constants import (
    Config,
    AgentMessages,
    ClientMessages
)


def _send_agent_notification(instance, email_type, message):

    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=instance.referred_by.email,
        text_template=AgentMessages.TEXT_USER_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_USER_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.referred_by.first_name,
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_client_notification(instance, email_type, message):
    referrer = "a test user"

    if instance.referred_by.first_name or instance.referred_by.last_name:
        fullname = list(filter(None, [instance.referred_by.first_name,
                                      instance.referred_by.last_name]))
        referrer = " ".join(fullname)

    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=instance.invited_user.email,
        text_template=ClientMessages.TEXT_USER_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=ClientMessages.HTML_USER_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.invited_user.first_name,
            "message": f"{message} {referrer}",
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()

from core.utils import HomeswiprMailer
from .constants import (
    Config,
    ClientMessages,
    AgentMessages,
    AdminMessages
)


def _send_client_notification(instance, email_type, message):
    client = instance.user
    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=client.email,
        text_template=ClientMessages.TEXT_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=ClientMessages.HTML_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": client.first_name,
            "saved_search_url": Config.FRONT_END_SAVED_SEARCH_URL + "/{}".format(instance.id),
            "saved_search_title": instance.title,
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_agent_notification(instance, email_type, message, agents=None):
    for agent in instance.agents.all():
        if agents:
            if agent.email in agents:
                message = AgentMessages.AGENT_ASSIGNMENT_SELF_MESSAGE
            else:
                message = AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE

        mail = HomeswiprMailer(
            subject=Config.EMAIL_SUBJECT,
            recipient=agent.email,
            text_template=AgentMessages.TEXT_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE,
            html_template=AgentMessages.HTML_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE,
            context={
                "user": agent.first_name,
                "saved_search_url": Config.FRONT_END_SAVED_SEARCH_URL + "/{}".format(instance.id),
                "saved_search_title": instance.title,
                "message": message,
                "root_url": Config.ROOT_URL,
                "email_type": email_type
            },
        )
        mail.send_mail()


def _send_admin_notification(instance, email_type, message):
    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=Config.ADMIN_EMAIL,
        text_template=AdminMessages.TEXT_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AdminMessages.HTML_SAVED_SEARCH_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "saved_search_url": Config.FRONT_END_SAVED_SEARCH_URL + "/{}".format(instance.id),
            "saved_search_title": instance.title,
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()

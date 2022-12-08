from core.utils import HomeswiprMailer
from .constants import (
    Config,
    ClientMessages,
    AgentMessages,
    AdminMessages
)


def _send_client_notification(instance, email_type, message):
    if hasattr(instance, 'booking'):
        mail = HomeswiprMailer(
            subject=Config.EMAIL_SUBJECT,
            recipient=instance.email,
            text_template=ClientMessages.TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
            html_template=ClientMessages.HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
            context={
                "user": instance.first_name,
                "property_url": Config.FRONT_END_PROPERTY_URL + "/{}".format(instance.booking.booked_property.id),
                "property_name": instance.booking.booked_property.related_address,
                "message": message,
                "root_url": Config.ROOT_URL,
                "email_type": email_type
            },
        )
        mail.send_mail()

    else:
        for client in instance.booking_client.all():
            mail = HomeswiprMailer(
                subject=Config.EMAIL_SUBJECT,
                recipient=client.email,
                text_template=ClientMessages.TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
                html_template=ClientMessages.HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
                context={
                    "user": client.first_name,
                    "property_url": Config.FRONT_END_PROPERTY_URL + "/{}".format(instance.booked_property.id),
                    "property_name": instance.booked_property.related_address,
                    "message": message,
                    "root_url": Config.ROOT_URL,
                    "email_type": email_type
                },
            )
            mail.send_mail()


def _send_agent_notification(instance, email_type, message, agents=None):
    if hasattr(instance, 'booking'):
        agent_instance = instance.booking.agents.all()
        booking_instance = instance.booking
    else:
        agent_instance = instance.agents.all()
        booking_instance = instance

    for agent in agent_instance:
        if agents:
            if agent.email in agents:
                message = AgentMessages.AGENT_ASSIGNMENT_SELF_MESSAGE
            else:
                message = AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE

        mail = HomeswiprMailer(
            subject=Config.EMAIL_SUBJECT,
            recipient=agent.email,
            text_template=AgentMessages.TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
            html_template=AgentMessages.HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
            context={
                "user": agent.first_name,
                "property_url": Config.FRONT_END_PROPERTY_URL + "/{}".format(booking_instance.booked_property.id),
                "property_name": booking_instance.booked_property.related_address,
                "message": message,
                "root_url": Config.ROOT_URL,
                "email_type": email_type
            },
        )
        mail.send_mail()


def _send_admin_notification(instance, email_type, message):
    if hasattr(instance, 'booking'):
        booking_instance = instance.booking
    else:
        booking_instance = instance

    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=Config.ADMIN_EMAIL,
        text_template=AdminMessages.TEXT_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AdminMessages.HTML_PROPERTY_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "property_url": Config.FRONT_END_PROPERTY_URL + "/{}".format(booking_instance.booked_property.id),
            "property_name": booking_instance.booked_property.related_address,
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()

from core.utils import HomeswiprMailer
from .constants import (
    Config,
    AgentMessages,
    AdminMessages
)


def _send_admin_notification(instance, email_type, message):
    property_address = None
    msg = message

    if email_type == 'agent_assignment':
        deal_id = instance.deal.id
        if instance.deal.connected_property:
            property_address = instance.deal.connected_property.related_address
        elif instance.deal.address:
            property_address = instance.deal.address
    else:
        deal_id = instance.id
        if email_type == 'update_deal_status':
            msg = message + instance.status.name

        if instance.connected_property:
            property_address = instance.connected_property.related_address
        elif instance.address:
            property_address = instance.address

    mail = HomeswiprMailer(
        subject=f"{Config.EMAIL_SUBJECT} {property_address}",
        recipient=Config.ADMIN_EMAIL,
        text_template=AdminMessages.TEXT_DEAL_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AdminMessages.HTML_DEAL_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "deal_url": Config.FRONT_END_DEAL_URL + "/{}".format(deal_id),
            "message": msg,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_creator_notification(instance, email_type, message):
    property_address = None

    if instance.connected_property:
        property_address = instance.connected_property.related_address
    elif instance.address:
        property_address = instance.address

    mail = HomeswiprMailer(
        subject=f"{Config.EMAIL_SUBJECT} {property_address}",
        recipient=instance.created_by.email,
        text_template=AgentMessages.TEXT_DEAL_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_DEAL_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.created_by.first_name,
            "deal_url": Config.FRONT_END_DEAL_URL + "/{}".format(instance.id),
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_agent_notification(instance, email_type, message):
    msg = message
    property_address = None

    if instance.deal.connected_property:
        property_address = instance.deal.connected_property.related_address
    elif instance.deal.address:
        property_address = instance.deal.address

    if email_type == 'update_deal_status':
        msg = message + instance.deal.status.name

    mail = HomeswiprMailer(
        subject=f"{Config.EMAIL_SUBJECT} {property_address}",
        recipient=instance.agent.email,
        text_template=AgentMessages.TEXT_DEAL_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_DEAL_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.agent.first_name,
            "deal_url": Config.FRONT_END_DEAL_URL + "/{}".format(instance.deal.id),
            "message": msg,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()

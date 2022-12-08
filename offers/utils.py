from core.utils import HomeswiprMailer
from .constants import (
    Config,
    AgentMessages,
    AdminMessages,
    StepsMessages
)
from .models import (
    OfferClient,
    Deposit,
    Condition,
    AdditionalTerm
)


def _send_admin_notification(instance, email_type, message):
    property_address = None
    msg = message

    if email_type == 'agent_assignment':
        offer_id = instance.property_offer.id
        if instance.property_offer.connected_property:
            property_address = instance.property_offer.connected_property.related_address
        elif instance.property_offer.address:
            property_address = instance.property_offer.address
    else:
        offer_id = instance.id
        if email_type == 'update_offer_status':
            msg = message + instance.offer_status.name

        if instance.connected_property:
            property_address = instance.connected_property.related_address
        elif instance.address:
            property_address = instance.address

    mail = HomeswiprMailer(
        subject=f"{Config.EMAIL_SUBJECT} {property_address}",
        recipient=Config.ADMIN_EMAIL,
        text_template=AdminMessages.TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AdminMessages.HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "offer_url": Config.FRONT_END_OFFER_URL + "/view/{}".format(offer_id),
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
        text_template=AgentMessages.TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.created_by.first_name,
            "offer_url": Config.FRONT_END_OFFER_URL + "/view/{}".format(instance.id),
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_agent_notification(instance, email_type, message):
    msg = message
    property_address = None

    if instance.property_offer.connected_property:
        property_address = instance.property_offer.connected_property.related_address
    elif instance.property_offer.address:
        property_address = instance.property_offer.address

    if email_type == 'update_offer_status':
        msg = message + instance.property_offer.offer_status.name

    mail = HomeswiprMailer(
        subject=f"{Config.EMAIL_SUBJECT} {property_address}",
        recipient=instance.agent.email,
        text_template=AgentMessages.TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.agent.first_name,
            "offer_url": Config.FRONT_END_OFFER_URL + "/view/{}".format(instance.property_offer.id),
            "message": msg,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_steps_notification(instance, email_type):
    user = None
    agent_name = None
    property_address = None
    clients = OfferClient.objects.filter(property_offer=instance.property_offer, type=instance.representing)
    initial_deposits = Deposit.objects.filter(property_offer=instance.property_offer, is_additional=False)
    additional_deposits = Deposit.objects.filter(property_offer=instance.property_offer, is_additional=True)
    conditions = Condition.objects.filter(property_offer=instance.property_offer)
    additional_terms = AdditionalTerm.objects.filter(property_offer=instance.property_offer)

    if instance.agent.first_name or instance.agent.last_name:
        fullname = list(filter(None, [instance.agent.first_name,
                                      instance.agent.last_name]))
        agent_name = " ".join(fullname)
        user = instance.agent.first_name
    elif instance.agent.full_name:
        agent_name = instance.agent.full_name
        user = instance.agent.full_name

    if instance.property_offer.connected_property:
        property_address = instance.property_offer.connected_property.related_address
    elif instance.property_offer.address:
        property_address = instance.property_offer.address

    mail = HomeswiprMailer(
        subject=f"{Config.EMAIL_SUBJECT} {property_address}",
        recipient=instance.agent.email,
        text_template=StepsMessages.TEXT_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=StepsMessages.HTML_OFFER_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": user,
            "agent_name": agent_name,
            "agent_email": instance.agent.email,
            "representing": instance.representing,
            "clients": clients,
            "property_address": property_address,
            "offer_amount": instance.property_offer.offer_amount,
            "closing_date": instance.property_offer.closing_date,
            "offer_open_till": instance.property_offer.offer_open_till,
            "initial_deposits": initial_deposits,
            "additional_deposits": additional_deposits,
            "conditions": conditions,
            "additional_terms": additional_terms,
            "offer_url": Config.FRONT_END_OFFER_URL + "/view/{}".format(instance.property_offer.id),
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()

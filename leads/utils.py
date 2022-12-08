from core.utils import HomeswiprMailer
from .constants import (
    Config,
    AgentMessages,
    AdminMessages
)


def _send_admin_notification(instance, email_type, message):
    deal_id = None

    if email_type == 'new_offer':
        deal_id = instance.id
    elif email_type == 'agent_assignment' or email_type == 'agent_unassigned':
        deal_id = instance.lead.id
    elif email_type == 'mortgage_assignment' or email_type == 'mortgage_unassigned':
        deal_id = instance.lead.id
    elif email_type == 'sales_agent_assignment' or email_type == 'sales_agent_unassigned':
        deal_id = instance.lead.id

    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=Config.ADMIN_EMAIL,
        text_template=AdminMessages.TEXT_LEAD_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AdminMessages.HTML_LEAD_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "lead_url": Config.FRONT_END_LEAD_URL + "/edit/{}".format(deal_id),
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_creator_notification(instance, email_type, message):
    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=instance.created_by.email,
        text_template=AgentMessages.TEXT_LEAD_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_LEAD_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": instance.created_by.first_name,
            "lead_url": Config.FRONT_END_LEAD_URL + "/edit/{}".format(instance.id),
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()


def _send_agent_notification(instance, email_type, message):
    agent = None

    if email_type == 'agent_assignment' or email_type == 'agent_unassigned':
        agent = instance.agent_assigned
    elif email_type == 'mortgage_assignment' or email_type == 'mortgage_unassigned':
        agent = instance.mortgage_broker
    elif email_type == 'sales_agent_assignment' or email_type == 'sales_agent_unassigned':
        agent = instance.sales_agent

    mail = HomeswiprMailer(
        subject=Config.EMAIL_SUBJECT,
        recipient=agent.email,
        text_template=AgentMessages.TEXT_LEAD_NOTIFICATION_EMAIL_TEMPLATE,
        html_template=AgentMessages.HTML_LEAD_NOTIFICATION_EMAIL_TEMPLATE,
        context={
            "user": agent.first_name,
            "lead_url": Config.FRONT_END_LEAD_URL + "/edit/{}".format(instance.lead.id),
            "message": message,
            "root_url": Config.ROOT_URL,
            "email_type": email_type
        },
    )
    mail.send_mail()

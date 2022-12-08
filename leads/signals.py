from django.utils import timezone
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from leads.models import (
    LeadAgents,
    LeadMortgageBroker,
    LeadSalesAgent
)

from .utils import (
    _send_admin_notification,
    _send_creator_notification,
    _send_agent_notification
)

from .constants import (
    EmailType,
    AgentMessages,
    AdminMessages
)


class LeadsSignal(object):
    """
    Signal for Leads to trigger send email notification on each successful database transaction.
    """

    @receiver(post_save, sender="leads.Lead", dispatch_uid="leads.models.Lead")
    def trigger_lead_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.NEW_LEAD,
                                                                       AdminMessages.NEW_LEAD_MESSAGE))
                if instance.created_by.email:
                    transaction.on_commit(lambda: _send_creator_notification(instance, EmailType.NEW_LEAD,
                                                                             AgentMessages.NEW_LEAD_MESSAGE))

    @receiver(post_save, sender="leads.LeadAgents", dispatch_uid="leads.models.LeadAgents")
    def trigger_lead_agent_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                lead_agents = LeadAgents.active_objects.filter(lead=instance.lead).exclude(
                    agent_assigned=instance.agent_assigned)
                if instance.agent_assigned and instance.agent_assigned.email:
                    transaction.on_commit(lambda: _send_agent_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                           AgentMessages.AGENT_ASSIGNMENT_SELF_MESSAGE))
                for agent in lead_agents:
                    if agent.agent_assigned and agent.agent_assigned.email:
                        transaction.on_commit(lambda: _send_agent_notification(
                            agent,
                            EmailType.AGENT_ASSIGNMENT,
                            AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE
                        ))
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                       AdminMessages.AGENT_ASSIGNMENT_MESSAGE))

    @receiver(post_save, sender="leads.LeadMortgageBroker", dispatch_uid="leads.models.LeadMortgageBroker")
    def trigger_lead_mortgage_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                lead_mortgage = LeadMortgageBroker.active_objects.filter(lead=instance.lead).exclude(
                    mortgage_broker=instance.mortgage_broker)
                if instance.mortgage_broker and instance.mortgage_broker.email:
                    transaction.on_commit(lambda: _send_agent_notification(
                        instance, EmailType.MORTGAGE_ASSIGNMENT, AgentMessages.MORTGAGE_ASSIGNMENT_SELF_MESSAGE))
                for agent in lead_mortgage:
                    if agent.mortgage_broker and agent.mortgage_broker.email:
                        transaction.on_commit(lambda: _send_agent_notification(
                            agent,
                            EmailType.MORTGAGE_ASSIGNMENT,
                            AgentMessages.MORTGAGE_ASSIGNMENT_ALL_MESSAGE
                        ))
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.MORTGAGE_ASSIGNMENT,
                                                                       AdminMessages.MORTGAGE_ASSIGNMENT_MESSAGE))

    @receiver(post_save, sender="leads.LeadSalesAgent", dispatch_uid="leads.models.LeadSalesAgent")
    def trigger_lead_sales_agent_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                lead_sales_agents = LeadSalesAgent.active_objects.filter(lead=instance.lead).exclude(
                    sales_agent=instance.sales_agent)
                if instance.sales_agent and instance.sales_agent.email:
                    transaction.on_commit(lambda: _send_agent_notification(
                        instance, EmailType.SALES_AGENT_ASSIGNMENT, AgentMessages.SALES_AGENT_ASSIGNMENT_SELF_MESSAGE))
                for agent in lead_sales_agents:
                    if agent.sales_agent and agent.sales_agent.email:
                        transaction.on_commit(lambda: _send_agent_notification(
                            agent,
                            EmailType.SALES_AGENT_ASSIGNMENT,
                            AgentMessages.SALES_AGENT_ASSIGNMENT_ALL_MESSAGE
                        ))
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.SALES_AGENT_ASSIGNMENT,
                                                                       AdminMessages.SALES_AGENT_ASSIGNMENT_MESSAGE))

    @receiver(post_delete, sender="leads.LeadAgents", dispatch_uid="leads.models.LeadAgents")
    def trigger_lead_agent_delete_email_notification(sender, instance, *args, **kwargs):
        with transaction.atomic():
            if instance.agent_assigned and instance.agent_assigned.email:
                transaction.on_commit(lambda: _send_agent_notification(instance, EmailType.AGENT_UNASSIGNED,
                                                                       AgentMessages.AGENT_UNASSIGNED_MESSAGE))
            transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                   AdminMessages.AGENT_UNASSIGNED_MESSAGE))

    @receiver(post_delete, sender="leads.LeadMortgageBroker", dispatch_uid="leads.models.LeadMortgageBroker")
    def trigger_lead_mortgage_delete_email_notification(sender, instance, *args, **kwargs):
        with transaction.atomic():
            if instance.mortgage_broker and instance.mortgage_broker.email:
                transaction.on_commit(lambda: _send_agent_notification(instance, EmailType.MORTGAGE_UNASSIGNED,
                                                                       AgentMessages.MORTGAGE_UNASSIGNED_MESSAGE))
            transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.MORTGAGE_UNASSIGNED,
                                                                   AdminMessages.AGENT_UNASSIGNED_MESSAGE))

    @receiver(post_delete, sender="leads.LeadSalesAgent", dispatch_uid="leads.models.LeadSalesAgent")
    def trigger_lead_sales_agent_delete_email_notification(sender, instance, *args, **kwargs):
        with transaction.atomic():
            if instance.sales_agent and instance.sales_agent.email:
                transaction.on_commit(lambda: _send_agent_notification(instance, EmailType.SALES_AGENT_UNASSIGNED,
                                                                       AgentMessages.SALES_AGENT_UNASSIGNED_MESSAGE))
            transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.SALES_AGENT_UNASSIGNED,
                                                                   AdminMessages.SALES_AGENT_UNASSIGNED_MESSAGE))

    @receiver(post_save, sender="leads.Note", dispatch_uid="leads.models.Note")
    def trigger_lead_note(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                instance.unread_note.create(
                    user=instance.history.first().history_user,
                    last_date_viewed=timezone.now(),
                    content_object=instance
                )

from django.utils import timezone
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from deal.models import Realtor

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


class DealsSignal(object):
    """
    Signal for Deals to trigger send email notification on each successful database transaction.
    """

    @receiver(post_save, sender="deal.Deal", dispatch_uid="deal.models.Deal")
    def trigger_deal_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            tracker = instance.tracker
            if created:
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.NEW_DEAL,
                                                                       AdminMessages.NEW_DEAL_MESSAGE))
                if instance.created_by.email:
                    transaction.on_commit(lambda: _send_creator_notification(instance, EmailType.NEW_DEAL,
                                                                             AgentMessages.NEW_DEAL_MESSAGE))
            else:
                if tracker.has_changed('status_id') and tracker.previous('status_id') != instance.status_id:
                    transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.UPDATE_DEAL_STATUS,
                                                                           AdminMessages.UPDATE_DEAL_STATUS_MESSAGE))
                    deal_agents = Realtor.active_objects.filter(deal=instance)
                    for agent in deal_agents:
                        if agent.agent and agent.agent.email:
                            transaction.on_commit(lambda: _send_agent_notification(
                                agent,
                                EmailType.UPDATE_DEAL_STATUS,
                                AgentMessages.UPDATE_DEAL_STATUS_MESSAGE
                            ))
                else:
                    transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.UPDATE_DEAL,
                                                                           AdminMessages.UPDATE_DEAL_MESSAGE))
                    deal_agents = Realtor.active_objects.filter(deal=instance)
                    for agent in deal_agents:
                        if agent.agent and agent.agent.email:
                            transaction.on_commit(lambda: _send_agent_notification(
                                agent,
                                EmailType.UPDATE_DEAL,
                                AgentMessages.UPDATE_DEAL_MESSAGE
                            ))

    @receiver(post_save, sender="deal.Realtor", dispatch_uid="deal.models.Realtor")
    def trigger_deal_agent_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                deal_agents = Realtor.active_objects.filter(deal=instance.deal).exclude(agent=instance.agent)
                if instance.agent and instance.agent.email:
                    transaction.on_commit(lambda: _send_agent_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                           AgentMessages.AGENT_ASSIGNMENT_SELF_MESSAGE))
                for agent in deal_agents:
                    if agent.agent and agent.agent.email:
                        transaction.on_commit(lambda: _send_agent_notification(
                            agent,
                            EmailType.AGENT_ASSIGNMENT,
                            AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE
                        ))
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                       AdminMessages.AGENT_ASSIGNMENT_MESSAGE))

    @receiver(post_save, sender="deal.DealNote", dispatch_uid="deal.models.DealNote")
    def trigger_deal_note(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                instance.unread_note.create(
                    user=instance.created_by,
                    last_date_viewed=timezone.now(),
                    content_object=instance
                )

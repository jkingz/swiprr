from django.utils import timezone
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from offers.models import OfferAgent

from .utils import (
    _send_admin_notification,
    _send_creator_notification,
    _send_agent_notification,
    _send_steps_notification
)

from .constants import (
    EmailType,
    AgentMessages,
    AdminMessages
)


class OffersSignal(object):
    """
    Signal for Offers to trigger send email notification on each successful database transaction.
    """

    @receiver(post_save, sender="offers.Offer", dispatch_uid="offers.models.Offer")
    def trigger_offer_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            tracker = instance.tracker
            if created:
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.NEW_OFFER,
                                                                       AdminMessages.NEW_OFFER_MESSAGE))
                if instance.created_by.email:
                    transaction.on_commit(lambda: _send_creator_notification(instance, EmailType.NEW_OFFER,
                                                                             AgentMessages.NEW_OFFER_MESSAGE))
            else:
                if tracker.has_changed('offer_status_id') and \
                        tracker.previous('offer_status_id') != instance.offer_status_id:
                    transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.UPDATE_OFFER_STATUS,
                                                                           AdminMessages.UPDATE_OFFER_STATUS_MESSAGE))
                    offer_agents = OfferAgent.active_objects.filter(property_offer=instance)
                    for agent in offer_agents:
                        if agent.agent and agent.agent.email:
                            transaction.on_commit(lambda: _send_agent_notification(
                                agent,
                                EmailType.UPDATE_OFFER_STATUS,
                                AgentMessages.UPDATE_OFFER_STATUS_MESSAGE
                            ))
                else:
                    transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.UPDATE_OFFER,
                                                                           AdminMessages.UPDATE_OFFER_MESSAGE))
                    offer_agents = OfferAgent.active_objects.filter(property_offer=instance)
                    for agent in offer_agents:
                        if agent.agent and agent.agent.email:
                            transaction.on_commit(lambda: _send_agent_notification(
                                agent,
                                EmailType.UPDATE_OFFER,
                                AgentMessages.UPDATE_OFFER_MESSAGE
                            ))

    @receiver(post_save, sender="offers.OfferAgent", dispatch_uid="offers.models.OfferAgent")
    def trigger_offer_agent_email_notification(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                offer_agents = OfferAgent.active_objects.filter(
                    property_offer=instance.property_offer).exclude(agent=instance.agent)
                if instance.agent and instance.agent.email:
                    transaction.on_commit(lambda: _send_agent_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                           AgentMessages.AGENT_ASSIGNMENT_SELF_MESSAGE))
                    transaction.on_commit(lambda: _send_steps_notification(instance, EmailType.OFFER_STEPS))
                for agent in offer_agents:
                    if agent.agent and agent.agent.email:
                        transaction.on_commit(lambda: _send_agent_notification(
                            agent,
                            EmailType.AGENT_ASSIGNMENT,
                            AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE
                        ))
                transaction.on_commit(lambda: _send_admin_notification(instance, EmailType.AGENT_ASSIGNMENT,
                                                                       AdminMessages.AGENT_ASSIGNMENT_MESSAGE))

    @receiver(post_save, sender="offers.OfferNote", dispatch_uid="offers.models.OfferNote")
    def trigger_offer_note(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                instance.unread_note.create(
                    user=instance.created_by,
                    last_date_viewed=timezone.now(),
                    content_object=instance
                )

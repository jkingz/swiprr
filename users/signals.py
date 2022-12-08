from django.db.models.signals import post_save
from django.dispatch import receiver

from components.models import Agent
from contacts.models import Contact

from .utils import (
    _send_agent_notification,
    _send_client_notification
)

from .constants import (
    EmailType,
    AgentMessages,
    ClientMessages
)


class UserSignal(object):
    """
    Signal for User to trigger creation of Agents and Contact for successful database transaction.
    """

    @receiver(post_save, sender="users.User", dispatch_uid="users.models.User")
    def trigger_contact_and_agent(sender, instance, created, **kwargs):
        if created:
            is_agent = instance.is_agent

            contact_instance, _ = Contact.objects.get_or_create(
                user_link=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
                phone_number=instance.phone_number,
                source="test.com",
                is_active=instance.is_active
            )

            if is_agent is True:
                agent_instance, _ = Agent.objects.get_or_create(
                    user=instance,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    email=instance.email,
                    phone_number=instance.phone_number,
                    is_active=instance.is_active
                )

        else:
            tracker = instance.tracker

            try:
                contact_instance = Contact.objects.get(user_link__id=instance.id)
            except Contact.DoesNotExist:
                contact_instance = None

            if contact_instance is not None:
                if tracker.has_changed('is_active') and tracker.previous('is_active') != instance.is_active:
                    contact_instance.is_active = instance.is_active
                    contact_instance.save()
            else:
                contact_instance, _ = Contact.objects.get_or_create(
                    user_link=instance,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    email=instance.email,
                    phone_number=instance.phone_number,
                    source="test.com",
                    is_active=instance.is_active
                )

            try:
                agent_instance = Agent.objects.get(user__id=instance.id)
            except Agent.DoesNotExist:
                agent_instance = None

            if agent_instance is not None:
                if (tracker.has_changed('is_agent') and tracker.previous('is_agent') != instance.is_agent) or \
                        (tracker.has_changed('is_active') and tracker.previous('is_active') != instance.is_active):
                    if instance.is_agent is True:
                        agent_instance.is_active = instance.is_active
                        agent_instance.save()
                    else:
                        agent_instance.is_active = instance.is_agent
                        agent_instance.save()
            else:
                if (tracker.has_changed('is_agent') and tracker.previous('is_agent') != instance.is_agent) and \
                        instance.is_agent is True:
                    agent_instance, _ = Agent.objects.get_or_create(
                        user=instance,
                        first_name=instance.first_name,
                        last_name=instance.last_name,
                        email=instance.email,
                        phone_number=instance.phone_number,
                        is_active=instance.is_active
                    )

    @receiver(post_save, sender="users.Referral", dispatch_uid="users.models.Referral")
    def trigger_referral_contact(sender, instance, created, **kwargs):
        if created:
            try:
                contact_instance = Contact.objects.get(user_link=instance.invited_user)
            except Contact.DoesNotExist:
                contact_instance = None

            referrer = instance.referred_by.email

            if contact_instance:
                if referrer:
                    contact_instance.source = f"test.com - {referrer}"
                else:
                    contact_instance.source = f"test.com"

                contact_instance.save()

            if instance.referred_by and instance.referred_by.email:
                _send_agent_notification(instance, EmailType.REFERRAL,
                                         AgentMessages.REFERRAL_MESSAGE)

            if instance.invited_user and instance.invited_user.email:
                _send_client_notification(instance, EmailType.REFERRAL,
                                          ClientMessages.REFERRAL_MESSAGE)

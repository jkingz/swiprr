from django import dispatch
from django.db.models.signals import post_save, pre_delete
from django.db import transaction
from django.dispatch import receiver

from .utils import (
    _send_client_notification,
    _send_agent_notification,
    _send_admin_notification,
)

from .constants import (
    EmailType,
    ClientMessages,
    AgentMessages,
    AdminMessages
)


class SavedSearchSignal(object):
    """
    Signal for Saved Search to trigger send email notification on each successful database transaction.
    """

    @receiver(post_save, sender="homeswipr.UserSavedSearch", dispatch_uid="homeswipr.models.UserSavedSearch")
    def trigger_saved_search_email_notification(sender, instance, created, **kwargs):
        if created:

            _send_client_notification(instance, EmailType.NEW_SAVED_SEARCH, ClientMessages.NEW_SAVED_SEARCH_MESSAGE)
            _send_admin_notification(instance, EmailType.NEW_SAVED_SEARCH, AdminMessages.NEW_SAVED_SEARCH_MESSAGE)

        else:
            tracker = instance.tracker

            # For saved search update
            # We first check if the field has changed,
            # then check if the previous value is not the same with the new value.

            if tracker.has_changed('frequency') and tracker.previous('frequency') != instance.frequency:
                _send_client_notification(instance, EmailType.UPDATED_FREQUENCY_SAVED_SEARCH,
                                          ClientMessages.UPDATED_FREQUENCY_MESSAGE + instance.frequency)
                _send_agent_notification(instance, EmailType.UPDATED_FREQUENCY_SAVED_SEARCH,
                                         AgentMessages.UPDATED_FREQUENCY_MESSAGE + instance.frequency)
                _send_admin_notification(instance, EmailType.UPDATED_FREQUENCY_SAVED_SEARCH,
                                         AdminMessages.UPDATED_FREQUENCY_MESSAGE + instance.frequency)

            # if tracker.has_changed('title') and tracker.previous('title') != instance.title:
            #     _send_client_notification(instance, EmailType.UPDATED_TITLE_SAVED_SEARCH,
            #                               ClientMessages.UPDATED_TITLE_MESSAGE)
            #     _send_agent_notification(instance, EmailType.UPDATED_TITLE_SAVED_SEARCH,
            #                              AgentMessages.UPDATED_TITLE_MESSAGE)
            #     _send_admin_notification(instance, EmailType.UPDATED_TITLE_SAVED_SEARCH,
            #                              AdminMessages.UPDATED_TITLE_MESSAGE)

            if tracker.has_changed('is_active') and tracker.previous('is_active') != instance.is_active \
                    and instance.is_active is False:
                _send_client_notification(instance, EmailType.DELETED_SAVED_SEARCH,
                                          ClientMessages.DELETED_SAVED_SEARCH_MESSAGE)
                _send_agent_notification(instance, EmailType.DELETED_SAVED_SEARCH,
                                         AgentMessages.DELETED_SAVED_SEARCH_MESSAGE)
                _send_admin_notification(instance, EmailType.DELETED_SAVED_SEARCH,
                                         AdminMessages.DELETED_SAVED_SEARCH_MESSAGE)


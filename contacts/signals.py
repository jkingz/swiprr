from django.utils import timezone
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver


class ContactsSignal(object):
    """
    Signals for Contacts on every successful database transaction.
    """

    @receiver(post_save, sender="contacts.Note", dispatch_uid="contacts.models.Note")
    def trigger_contact_note(sender, instance, created, **kwargs):
        with transaction.atomic():
            if created:
                instance.unread_note.create(
                    user=instance.created_by,
                    last_date_viewed=timezone.now(),
                    content_object=instance
                )

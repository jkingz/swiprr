from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from rest_framework.exceptions import ValidationError

from model_utils import FieldTracker
from simple_history.models import HistoricalRecords
from core.models import CommonInfo
from contacts.constants import OPTIONAL

from components.models import UnreadNote, Email, PhoneNumber


class Contact(CommonInfo):
    """
    Database schema for contacts.
    first_name is set to optional since there is instances that the contact didn't provide any first_name.
    last_name is set to optional since there is instances that the contact didn't provide any first_name.
    middle is
    """

    first_name = models.CharField(max_length=300,  **OPTIONAL)
    last_name = models.CharField(max_length=300, **OPTIONAL)
    middle_name = models.CharField(max_length=300, **OPTIONAL)
    email = models.EmailField(**OPTIONAL)
    phone_number = models.CharField(max_length=15, **OPTIONAL)
    city = models.TextField(**OPTIONAL)
    associated_company = models.TextField(**OPTIONAL)
    occupation = models.CharField(max_length=300, **OPTIONAL)
    source = models.CharField(max_length=300, **OPTIONAL)
    user_link = models.OneToOneField('users.User', **OPTIONAL, related_name='contact_user',
                                             on_delete=models.CASCADE)
    additional_emails = GenericRelation(Email)
    additional_phone_numbers = GenericRelation(PhoneNumber)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"

    @property
    def has_lead(self):
        if self.leadcontact_set.all():
            return True
        else:
            return False

    def validate_contact(self):
        email = None
        phone_number = self.phone_number

        if self.email:
            email = self.email.lower()

        if email:
            _email = Contact.objects.filter(email=email)
            if _email.exists():
                if self.tracker.has_changed('email') and self.tracker.previous('email') != self.email:
                    if _email[0].is_active is True:
                        raise ValidationError({"email": "Email already exists"})
                    else:
                        raise ValidationError({"email": "Email already exists (Record is Archived)"})
        if phone_number:
            _phone_number = Contact.objects.filter(phone_number=phone_number)
            if _phone_number.exists():
                if self.tracker.has_changed('phone_number') and \
                        self.tracker.previous('phone_number') != self.phone_number:
                    if _phone_number[0].is_active is True:
                        raise ValidationError({"phone_number": "Phone number already exists"})
                    else:
                        raise ValidationError({"phone_number": "Phone number already exists (Record is Archived)"})
        if not (email or phone_number):
            raise ValidationError({"contact": "Please provide email or phone number"})

    def save(self, *args, **kwargs):
        self.validate_contact()
        super(Contact, self).save(*args, **kwargs)


class ContactAgent(CommonInfo):
    """
    This model is for the agent on a contact.
    """

    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, **OPTIONAL, related_name='contact_agent')
    agent = models.ForeignKey('components.Agent', on_delete=models.CASCADE, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.contact} - {self.agent}"


class ContactMortgageBroker(CommonInfo):
    """
    This model is for contact mortgage broker.
    """
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, **OPTIONAL, related_name='contact_mortgage_broker')
    mortgage_broker = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.contact} - {self.mortgage_broker}"


class Note(CommonInfo):
    """
    This model is for the notes on the contact.
    """

    contact = models.ForeignKey('contacts.Contact',  **OPTIONAL, on_delete=models.CASCADE, related_name='contact_note')
    note = models.TextField()
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)
    unread_note = GenericRelation(UnreadNote)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.contact} - ${self.note}"


class ContactSalesAgent(CommonInfo):
    """
    This model is for contact sales agent.
    """
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, **OPTIONAL, related_name='contact_sales_agent')
    sales_agent = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.contact} - {self.sales_agent}"

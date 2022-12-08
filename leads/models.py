from operator import mod
from pyexpat import model
from statistics import mode
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils import FieldTracker
from simple_history.models import HistoricalRecords

from core.models import CommonInfo
from core.constants import OPTIONAL

from components.models import UnreadNote


class Lead(CommonInfo):
    """
    """
    TRANSACTION_CHOICES = [
        ('Commercial', 'Commercial'),
        ('Residential', 'Residential'),
        ('Both', 'Both')
    ]

    financial_status = models.ForeignKey('leads.FinancialStatus', **OPTIONAL, related_name='financial_status', on_delete=models.SET_NULL)
    lead_status = models.ForeignKey('leads.LeadStatus', **OPTIONAL, related_name='lead_status', on_delete=models.SET_NULL)
    contact_type = models.ForeignKey('leads.ContactType', **OPTIONAL, related_name='contact_type', on_delete=models.SET_NULL)
    initial_contact_made = models.BooleanField(default=False)
    search_set = models.BooleanField(default=False)
    deals = models.BooleanField(default=False)
    offers = models.BooleanField(default=False)
    enroll_in_structurely = models.BooleanField(default=False)
    cma_created = models.BooleanField(default=False)
    cma_file_link = models.URLField(**OPTIONAL)
    client_criteria = models.TextField(**OPTIONAL)
    transaction_type = models.CharField(max_length=25, choices=TRANSACTION_CHOICES, **OPTIONAL)
    created_by = models.ForeignKey('users.User', **OPTIONAL, on_delete=models.SET_NULL)
    lead_warmth = models.ForeignKey('leads.LeadWarmth', **OPTIONAL, related_name='lead_warmth', on_delete=models.SET_NULL)
    time_frame = models.ForeignKey('leads.TimeFrame', **OPTIONAL, related_name='time_frame', on_delete=models.SET_NULL)
    market_report = models.BooleanField(default=False)
    property_address = models.CharField(max_length=1500, **OPTIONAL)
    is_flag = models.BooleanField(default=False)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.contact_type} - {self.financial_status}"


class LeadContact(CommonInfo):
    """
    Connection of contacts to leads.
    """
    contact = models.ForeignKey('contacts.Contact', **OPTIONAL, on_delete=models.CASCADE)
    lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.lead} - {self.contact}"


class LeadAgents(CommonInfo):
    """
    This model is for the lead. 
    """
    lead = models.ForeignKey('leads.Lead', **OPTIONAL, on_delete=models.CASCADE)
    agent_assigned = models.ForeignKey('components.Agent', **OPTIONAL, related_name='contact_agents', on_delete=models.CASCADE)
    history = HistoricalRecords()

    tracker = FieldTracker()

    class Meta:
        verbose_name_plural = "Lead Agents"

    def __str__(self):
        return f"{self.agent_assigned} - {self.lead}"


class Note(CommonInfo):
    """
    This model is for the notes on the lead.
    """
    note = models.TextField()
    lead = models.ForeignKey('leads.Lead',  **OPTIONAL, on_delete=models.CASCADE)
    unread_note = GenericRelation(UnreadNote)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.lead} - ${self.note}"


class LeadStatus(CommonInfo):
    """
    This model is for the lead status on lead.
    """
    name = models.CharField(max_length=300)
    index = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Lead Status"

    def __str__(self):
        return f"{self.name}"


class ContactType(CommonInfo):
    """
    This model is for the contact type on lead.
    """
    name = models.CharField(max_length=300)
    index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"


class FinancialStatus(CommonInfo):
    """
    This model is for the financial status on lead.
    """
    name = models.CharField(max_length=300)
    index = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Financial Status"

    def __str__(self):
        return f"{self.name}"


class LeadWarmth(CommonInfo):
    """
    This model is for the lead warmth on lead.
    """
    name = models.CharField(max_length=300)
    index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"


class TimeFrame(CommonInfo):
    """
    This model is for the time frame on lead.
    """
    range = models.CharField(max_length=300)
    index = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.range}"


class LeadMortgageBroker(CommonInfo):
    """
    """

    lead = models.ForeignKey('leads.Lead',  **OPTIONAL, on_delete=models.CASCADE)
    mortgage_broker = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL, related_name='lead_mortgage_broker')

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.lead} - {self.mortgage_broker}"


class LeadSalesAgent(CommonInfo):
    """
    """

    lead = models.ForeignKey('leads.Lead',  **OPTIONAL, on_delete=models.CASCADE)
    sales_agent = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL, related_name='lead_sales_agent')

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.lead} - {self.sales_agent}"

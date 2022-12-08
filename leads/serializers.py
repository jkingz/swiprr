import datetime
from asyncore import write
from dataclasses import field
from pyexpat import model
from django.db import transaction
from rest_framework import serializers

from users.models import User
from components.models import Agent
from components.serializers import AgentSerializer
from contacts.models import (
    Contact,
    ContactAgent,
    ContactSalesAgent,
    ContactMortgageBroker
)
from contacts.serializers import ContactSerializer
from core.utils import TimezoneManager
from leads.models import (
    Lead,
    LeadStatus,
    LeadContact,
    LeadAgents,
    FinancialStatus,
    Note,
    ContactType,
    LeadWarmth,
    TimeFrame,
    LeadMortgageBroker,
    LeadSalesAgent
)
from users.serializers import UserProfileSerializer
from components.models import UnreadNote


class TimeFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeFrame
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = TimeFrame.objects.get_or_create(range=validated_data.get('range'))

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.range = validated_data.get('range', instance.range)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class LeadWarmthSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadWarmth
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = LeadWarmth.objects.get_or_create(name=validated_data.get('name'))

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class ContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactType
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = ContactType.objects.get_or_create(name=validated_data.get('name'))

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance


class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatus
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = LeadStatus.objects.get_or_create(name=validated_data.get('name'))

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance


class FinancialStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialStatus
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = FinancialStatus.objects.get_or_create(name=validated_data.get('name'))

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance


class NoteSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer(required=False, read_only=True)

    class Meta:
        model = Note
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = Note.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.lead = validated_data.get('lead', instance.lead)
        instance.note = validated_data.get('note', instance.note)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(NoteSerializer, self).to_representation(instance)

        data.update({
            'creator': UserProfileSerializer(instance.history.first().history_user).data,
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated)
        })
        return data


class LeadAgentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadAgents
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = LeadAgents.objects.get_or_create(**validated_data)
        lead_contact = LeadContact.objects.filter(lead=validated_data.get('lead'))

        if lead_contact:
            for contact in lead_contact:
                ContactAgent.objects.get_or_create(
                    contact=contact.contact,
                    agent=instance.agent_assigned
                )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.lead = validated_data.get('lead', instance.lead)
        instance.agent_assigned = validated_data.get('agent_assigned', instance.agent_assigned)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(LeadAgentsSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class LeadMortgageBrokerSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False, read_only=True, source="mortgage_broker")

    class Meta:
        model = LeadMortgageBroker
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = LeadMortgageBroker.objects.get_or_create(**validated_data)
        lead_contact = LeadContact.objects.filter(lead=validated_data.get('lead'))

        if lead_contact:
            for contact in lead_contact:
                ContactMortgageBroker.objects.get_or_create(
                    contact=contact.contact,
                    mortgage_broker=instance.mortgage_broker
                )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(LeadMortgageBrokerSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class LeadSalesAgentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False, read_only=True, source="sales_agent")

    class Meta:
        model = LeadSalesAgent
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = LeadSalesAgent.objects.get_or_create(**validated_data)
        lead_contact = LeadContact.objects.filter(lead=validated_data.get('lead'))

        if lead_contact:
            for contact in lead_contact:
                ContactSalesAgent.objects.get_or_create(
                    contact=contact.contact,
                    sales_agent=instance.sales_agent
                )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(LeadSalesAgentSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class LeadSerializer(serializers.ModelSerializer):
    contacts = serializers.ListField(child=serializers.IntegerField(), required=False,  write_only=True)
    mortgage_brokers = serializers.ListField(child=serializers.IntegerField(), required=False,  write_only=True)
    sales_agents = serializers.ListField(child=serializers.IntegerField(), required=False,  write_only=True)
    agent = serializers.ListField(child=serializers.IntegerField(), required=False,  write_only=True)
    notes = NoteSerializer(many=True, required=False, write_only=True, source="note")
    assign_agent = LeadAgentsSerializer(many=True, required=False, write_only=True, source="leadagents")

    # agents = LeadAgentsSerializer(many=True, read_only=True, source="leadagents_set")
    clients = ContactSerializer(many=True, read_only=True, source="leadcontact_set")
    contact_types = ContactTypeSerializer(read_only=True, source="contact_type")
    lead_statuses = LeadStatusSerializer(read_only=True, source="lead_status")
    financial_statuses = FinancialStatusSerializer(read_only=True, source="financial_status")
    lead_warmths = LeadWarmthSerializer(read_only=True, source="lead_warmth")
    time_frames = TimeFrameSerializer(read_only=True, source="time_frame")
    # lead_notes = NoteSerializer(many=True, read_only=True, source="note_set")
    agents = AgentSerializer(many=True, read_only=True, source="leadagents_set")
    lead_day_tracker = serializers.SerializerMethodField()
    assigned_mortgage_brokers = LeadMortgageBrokerSerializer(many=True, read_only=True, source="leadmortgagebroker_set")
    assigned_sales_agents = LeadSalesAgentSerializer(many=True, read_only=True, source="leadsalesagent_set")

    class Meta:
        model = Lead
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        contacts = validated_data.pop('contacts', None)
        agents = validated_data.pop('agent', None)
        notes = self.initial_data.get("note", None)
        mortgage_brokers = validated_data.pop('mortgage_brokers', None)
        sales_agents = validated_data.pop('sales_agents', None)
        _created_by = self.context.get("request").user

        instance = Lead.objects.create(created_by=_created_by, **validated_data)

        if contacts:
            for contact in contacts:
                contact_instance = Contact.objects.get(id=contact)
                LeadContact.objects.get_or_create(contact=contact_instance, lead=instance)
                if _created_by.is_agent:
                    agent_instance, _ = ContactAgent.objects.get_or_create(
                        contact=contact_instance,
                        agent=Agent.objects.get(user=_created_by)
                    )

                if _created_by.user_type and _created_by.user_type.type == 'Mortgage Broker':
                    ContactMortgageBroker.objects.get_or_create(
                        contact=contact_instance,
                        mortgage_broker=_created_by
                    )

                if _created_by.user_type and _created_by.user_type.type == 'Sales Agent':
                    ContactSalesAgent.objects.get_or_create(
                        contact=contact_instance,
                        sales_agent=_created_by
                    )

                if agents:
                    for agent in agents:
                        ContactAgent.objects.get_or_create(
                            contact=contact_instance,
                            agent_id=agent
                        )

                if mortgage_brokers:
                    for mortgage_broker in mortgage_brokers:
                        ContactMortgageBroker.objects.get_or_create(
                            contact=contact_instance,
                            mortgage_broker=User.objects.get(id=int(mortgage_broker))
                        )

                if sales_agents:
                    for sales_agent in sales_agents:
                        ContactSalesAgent.objects.get_or_create(
                            contact=contact_instance,
                            sales_agent=User.objects.get(id=int(sales_agent))
                        )

        if notes:
            for note in notes:
                note = note.get('notes')
                if note:
                    Note.objects.get_or_create(note=note, lead=instance)

        if _created_by.is_agent:
            LeadAgents.objects.get_or_create(
                lead=instance,
                agent_assigned=Agent.objects.get(user=_created_by)
            )

        if _created_by.user_type and _created_by.user_type.type == 'Mortgage Broker':
            LeadMortgageBroker.objects.get_or_create(
                lead=instance,
                mortgage_broker=_created_by
            )

        if _created_by.user_type and _created_by.user_type.type == 'Sales Agent':
            LeadSalesAgent.objects.get_or_create(
                lead=instance,
                sales_agent=_created_by
            )

        if mortgage_brokers:
            for mortgage_broker in mortgage_brokers:
                LeadMortgageBroker.objects.get_or_create(
                    lead=instance,
                    mortgage_broker=User.objects.get(id=int(mortgage_broker))
                )

        if sales_agents:
            for sales_agent in sales_agents:
                LeadSalesAgent.objects.get_or_create(
                    lead=instance,
                    sales_agent=User.objects.get(id=int(sales_agent))
                )

        if agents:
            for agent in agents:
                agent_instance = Agent.objects.get(id=agent)
                LeadAgents.objects.get_or_create(lead=instance, agent_assigned=agent_instance)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.financial_status = validated_data.get('financial_status', instance.financial_status)
        instance.lead_status = validated_data.get('lead_status', instance.lead_status)
        instance.contact_type = validated_data.get('contact_type', instance.contact_type)
        instance.initial_contact_made = validated_data.get('initial_contact_made', instance.initial_contact_made)
        instance.search_set = validated_data.get('search_set', instance.search_set)
        instance.deals = validated_data.get('deals', instance.deals)
        instance.offers = validated_data.get('offers', instance.offers)
        instance.enroll_in_structurely = validated_data.get('enroll_in_structurely', instance.enroll_in_structurely)
        instance.cma_created = validated_data.get('cma_created', instance.cma_created)
        instance.cma_file_link = validated_data.get('cma_file_link', instance.cma_file_link)
        instance.client_criteria = validated_data.get('client_criteria', instance.client_criteria)
        instance.transaction_type = validated_data.get('transaction_type', instance.transaction_type)
        instance.lead_warmth = validated_data.get('lead_warmth', instance.lead_warmth)
        instance.time_frame = validated_data.get('time_frame', instance.time_frame)
        instance.market_report = validated_data.get('market_report', instance.market_report)
        instance.property_address = validated_data.get('property_address', instance.property_address)
        instance.is_flag = validated_data.get('is_flag', instance.is_flag)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(LeadSerializer, self).to_representation(instance)
        contacts = Contact.objects.filter(leadcontact__lead=instance)
        agents = Agent.objects.filter(contact_agents__lead=instance)

        user = self.context.get("request").user
        object_id = Note.objects.filter(lead=instance).values_list('id')
        note = UnreadNote.objects.filter(user=user, object_id__in=object_id).order_by('-last_date_viewed').first()
        last_date_viewed = None if not note else TimezoneManager.localize_to_canadian_timezone(note.last_date_viewed)
        unread_count = len(object_id.filter(unread_note=None))

        data.update({
            'clients': ContactSerializer(contacts, many=True).data,
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
            'agents': AgentSerializer(agents, many=True).data,
            'notes_last_date_viewed': last_date_viewed,
            'unread_notes': unread_count,
        })

        return data

    @classmethod
    def get_lead_day_tracker(cls, obj):
        """
        Get lead day tracker.
        """

        _to = datetime.date.today()
        _from = datetime.date(obj.date_created.year,
                              obj.date_created.month,
                              obj.date_created.day)
        diff = _to - _from

        return diff.days


class LeadContactSerializer(serializers.ModelSerializer):
    leads = LeadSerializer(read_only=True, source="lead")

    class Meta:
        model = LeadContact
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = LeadContact.objects.get_or_create(**validated_data)
        lead_agent = LeadAgents.objects.filter(lead=validated_data.get('lead'))

        if lead_agent:
            for agent in lead_agent:
                contact_agent_instance, _ = ContactAgent.objects.get_or_create(
                    contact=instance.contact,
                    agent=agent.agent_assigned
                )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.lead = validated_data.get('lead', instance.lead)
        instance.contact = validated_data.get('contact', instance.contact)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(LeadContactSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data

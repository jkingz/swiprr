from django.db import transaction
from rest_framework import serializers

from users.models import User
from components.serializers import AgentSerializer
from components.models import Agent
from contacts.models import (
    Contact,
    ContactAgent,
    Note,
    ContactMortgageBroker,
    ContactSalesAgent
)
from core.utils import TimezoneManager
from users.serializers import UserProfileSerializer
from components.models import UnreadNote


class ContactAgentSerializer(serializers.ModelSerializer):
    """
    Agent for a specific contact serializer.
    """

    assigned_agent = AgentSerializer(required=False, read_only=True, source='agent')

    class Meta:
        model = ContactAgent
        fields = '__all__'

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = ContactAgent.objects.get_or_create(
            contact=validated_data.get('contact'),
            agent=validated_data.get('agent')
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(ContactAgentSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ContactMortgageBrokerSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False, read_only=True, source="mortgage_broker")

    class Meta:
        model = ContactMortgageBroker
        fields = '__all__'

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = ContactMortgageBroker.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """

        data = super(ContactMortgageBrokerSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ContactSalesAgentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(required=False, read_only=True, source="sales_agent")

    class Meta:
        model = ContactSalesAgent
        fields = '__all__'

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = ContactSalesAgent.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """

        data = super(ContactSalesAgentSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ContactNoteSerializer(serializers.ModelSerializer):
    """
    Note for a specific contact serializer.
    """

    user = UserProfileSerializer(required=False, read_only=True, source="created_by")

    class Meta:
        model = Note
        fields = '__all__'

    @transaction.atomic()
    def create(self, validated_data):
        _created_by = self.context.get("request").user

        instance, _ = Note.objects.get_or_create(
            contact=validated_data.get('contact'),
            note=validated_data.get('note'),
            created_by=_created_by
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        user = self.context.get("request").user
        created_by = instance.created_by

        if created_by == user:
            instance.note = validated_data.get('note', instance.note)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.save()
        else:
            raise serializers.ValidationError("User is not allowed to update this note")

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(ContactNoteSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ContactSerializer(serializers.ModelSerializer):
    """
    Contact serializer.
    """
    mortgage_brokers = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    sales_agents = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    contact_agents = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    assigned_agents = ContactAgentSerializer(many=True, required=False, source="contact_agent")
    # contact_notes = ContactNoteSerializer(many=True, required=False, source="contact_note")
    assigned_mortgage_brokers = ContactMortgageBrokerSerializer(many=True, required=False,
                                                                source="contact_mortgage_broker")
    assigned_sales_agents = ContactSalesAgentSerializer(many=True, required=False, source="contact_sales_agent")
    additional_emails = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    additional_phone_numbers = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)

    class Meta:
        model = Contact
        fields = ('id',
                  'first_name',
                  'last_name',
                  'middle_name',
                  'email',
                  'phone_number',
                  'city',
                  'associated_company',
                  'occupation',
                  'source',
                  'user_link',
                  'assigned_agents',
                  'contact_agents',
                  # 'contact_notes',
                  'has_lead',
                  'date_updated',
                  'date_created',
                  'is_active',
                  'mortgage_brokers',
                  'assigned_mortgage_brokers',
                  'sales_agents',
                  'assigned_sales_agents',
                  'additional_emails',
                  'additional_phone_numbers')

    @transaction.atomic
    def create(self, validated_data):
        contact_agent = validated_data.pop("contact_agents", [])
        contact_note = validated_data.pop("contact_note", [])
        _created_by = self.context.get("request").user
        mortgage_brokers = validated_data.pop("mortgage_brokers", [])
        sales_agents = validated_data.pop("sales_agents", [])
        additional_emails = validated_data.pop("additional_emails", [])
        additional_phone_numbers = validated_data.pop("additional_phone_numbers", [])

        try:
            user_payload = {}
            user = None
            if validated_data.get('email'):
                user_payload.update({'email': validated_data.get('email')})
            if validated_data.get('phone_number'):
                user_payload.update({'phone_number': validated_data.get('phone_number')})
            if user_payload:
                user = User.objects.get(**user_payload)
            if user:
                validated_data.update({'user_link': user})
        except User.DoesNotExist:
            pass

        instance, _ = Contact.objects.get_or_create(**validated_data)

        if _created_by.is_agent:
            contact_agent_instance, _ = ContactAgent.objects.get_or_create(
                contact=instance,
                agent=Agent.objects.get(user=_created_by)
            )

        if _created_by.user_type and _created_by.user_type.type == 'Mortgage Broker':
            contact_mortgage_broker_instance, _ = ContactMortgageBroker.objects.get_or_create(
                contact=instance,
                mortgage_broker=_created_by
            )

        if _created_by.user_type and _created_by.user_type.type == 'Sales Agent':
            contact_sales_agent_instance, _ = ContactSalesAgent.objects.get_or_create(
                contact=instance,
                sales_agent=_created_by
            )

        if contact_agent:
            for agent in contact_agent:
                contact_agent_instance, _ = ContactAgent.objects.get_or_create(
                    contact=instance,
                    agent_id=agent
                )

        if mortgage_brokers:
            for mortgage_broker in mortgage_brokers:
                contact_mortgage_broker_instance, _ = ContactMortgageBroker.objects.get_or_create(
                    contact=instance,
                    mortgage_broker=User.objects.get(id=int(mortgage_broker))
                )

        if sales_agents:
            for sales_agent in sales_agents:
                contact_sales_agent_instance, _ = ContactSalesAgent.objects.get_or_create(
                    contact=instance,
                    sales_agent=User.objects.get(id=int(sales_agent))
                )

        if contact_note:
            for note in contact_note:
                contact_note_instance, _ = Note.objects.get_or_create(
                    contact=instance,
                    note=note.get('note'),
                    created_by=_created_by
                )

        if additional_emails:
            for email in additional_emails:
                email_instance, _ = instance.additional_emails.get_or_create(
                    email=email
                )

        if additional_phone_numbers:
            for phone_number in additional_phone_numbers:
                phone_number_instance, _ = instance.additional_phone_numbers.get_or_create(
                    phone_number=phone_number
                )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.middle_name = validated_data.get('middle_name', instance.middle_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.city = validated_data.get('city', instance.city)
        instance.associated_company = validated_data.get('associated_company', instance.associated_company)
        instance.occupation = validated_data.get('occupation', instance.occupation)
        instance.source = validated_data.get('source', instance.source)
        instance.user_link = validated_data.get('user_link', instance.user_link)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        if validated_data.get('additional_emails', []):
            for email in validated_data.get('additional_emails', []):
                email_instance, _ = instance.additional_emails.get_or_create(
                    email=email
                )

        if validated_data.get('additional_phone_numbers', []):
            for phone_number in validated_data.get('additional_phone_numbers', []):
                phone_number, _ = instance.additional_phone_numbers.get_or_create(
                    phone_number=phone_number
                )

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(ContactSerializer, self).to_representation(instance)
        data_payload = {}

        if not hasattr(instance, 'contact') and self.context.get("request") is not None:
            user = self.context.get("request").user
            object_id = Note.objects.filter(contact=instance).values_list('id')
            note = UnreadNote.objects.filter(user=user, object_id__in=object_id).order_by('-last_date_viewed').first()
            last_date_viewed = None if not note else TimezoneManager.localize_to_canadian_timezone(note.last_date_viewed)
            unread_count = len(object_id.filter(unread_note=None))

            data_payload.update({
                'additional_emails': instance.additional_emails.values_list('email', flat=True),
                'additional_phone_numbers': instance.additional_phone_numbers.values_list('phone_number', flat=True),
                'notes_last_date_viewed': last_date_viewed,
                'unread_notes': unread_count,
            })

        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
            **data_payload
        })

        return data

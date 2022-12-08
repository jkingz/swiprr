from email.policy import default
from datetime import datetime, date, timedelta
import dateutil.parser

from django.db import transaction
from rest_framework import serializers
from core.utils import TimezoneManager
from offers.models import (
    Offer,
    OfferStatus,
    OfferClient,
    OfferAgent,
    OfferNote,
    Requirement,
    Condition,
    AdditionalTerm,
    Deposit,
    GoodsIncluded,
    OfferAdditionalDocuments
)
from components.models import Agent
from contacts.models import Contact
from contacts.serializers import ContactSerializer
from components.serializers import AgentSerializer
from users.serializers import UserProfileSerializer
from components.models import UnreadNote


class OfferStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferStatus
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = OfferStatus.objects.get_or_create(name=validated_data.get('name'))

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class OfferClientSerializer(serializers.ModelSerializer):
    """
    Buyer for a specific offer serializer.
    """

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.CharField(write_only=True, required=False, allow_null=True, default=None)
    phone_number = serializers.CharField(write_only=True, required=False, allow_null=True, default=None)
    client = ContactSerializer(read_only=True)

    class Meta:
        model = OfferClient
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        client_payload = {}
        email = validated_data.get('email', None)
        phone_number = validated_data.get('phone_number', None)

        if email or phone_number:
            if email:
                client_payload.update({'email': email.lower()})
            if phone_number:
                client_payload.update({'phone_number': phone_number})

            instance, _ = OfferClient.objects.get_or_create(
                property_offer=validated_data.get('property_offer'),
                client=Contact.objects.get_or_create(
                    first_name=validated_data.get('first_name'),
                    last_name=validated_data.get('last_name'),
                    **client_payload
                )[0],
                type="Buyer"
            )
        else:
            instance, _ = OfferClient.objects.get_or_create(
                property_offer=validated_data.get('property_offer'),
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                type="Buyer"
            )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.type = validated_data.get('type', instance.type)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        if not instance.client:
            instance.first_name = validated_data.get('first_name', instance.first_name)
            instance.last_name = validated_data.get('last_name', instance.last_name)

        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(OfferClientSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class OfferNoteSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = OfferNote
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        validated_data.update({
            'created_by': self.context.get("request").user
        })
        instance, _ = OfferNote.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic
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
        data = super(OfferNoteSerializer, self).to_representation(instance)
        data.update({
            'created_by': UserProfileSerializer(instance.created_by).data
        })

        return data


class OfferAdditionalDocumentsSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = OfferAdditionalDocuments
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        validated_data.update({
            'created_by': self.context.get("request").user
        })
        instance, _ = OfferAdditionalDocuments.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(OfferAdditionalDocumentsSerializer, self).to_representation(instance)
        data.update({
            'created_by': UserProfileSerializer(instance.created_by).data
        })

        return data


class OfferAgentSerializer(serializers.ModelSerializer):
    """
    Agent for a specific offer serializer.
    """

    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    agent = AgentSerializer(read_only=True)

    class Meta:
        model = OfferAgent
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        agent_payload = {}
        if validated_data.get('email'):
            agent_payload.update({'email': validated_data.get('email').lower()})
        if validated_data.get('phone_number'):
            agent_payload.update({'phone_number': validated_data.get('phone_number')})

        instance, _ = OfferAgent.objects.get_or_create(
            property_offer=validated_data.get('property_offer'),
            agent=Agent.objects.get_or_create(
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                **agent_payload
            )[0],
            representing=validated_data.get("representing")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.representing = validated_data.get('representing', instance.representing)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(OfferAgentSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class RequirementSerializer(serializers.ModelSerializer):
    """
    Requirement for a specific offer serializer.
    """

    class Meta:
        model = Requirement
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = Requirement.objects.get_or_create(
            property_offer=validated_data.get("property_offer"),
            image=validated_data.get("image"),
            note=validated_data.get("note")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.note = validated_data.get('note', instance.note)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(RequirementSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ConditionSerializer(serializers.ModelSerializer):
    """
    Condition for a specific offer serializer.
    """

    class Meta:
        model = Condition
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = Condition.objects.get_or_create(
            property_offer=validated_data.get("property_offer"),
            name=validated_data.get("name"),
            condition_date=validated_data.get("condition_date")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.condition_date = validated_data.get('condition_date', instance.condition_date)
        instance.status = validated_data.get('status', instance.status)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(ConditionSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        if instance.condition_date:
            data.update({
                'condition_date': TimezoneManager.localize_to_canadian_timezone(instance.condition_date)
            })

        return data


class AdditionalTermSerializer(serializers.ModelSerializer):
    """
    Additional term for a specific offer serializer.
    """

    class Meta:
        model = AdditionalTerm
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = AdditionalTerm.objects.get_or_create(
            property_offer=validated_data.get("property_offer"),
            name=validated_data.get("name")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(AdditionalTermSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class DepositSerializer(serializers.ModelSerializer):
    """
    Deposit for a specific offer serializer.
    """

    class Meta:
        model = Deposit
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        # The default value when deposit date is not provided it should be 3 days from current date of creation.
        default_deposit_date = date.today() + timedelta(days=3)
        deposit_date = validated_data.get("deposit_date") if validated_data.get("deposit_date") else default_deposit_date
        instance, _ = Deposit.objects.get_or_create(
            property_offer=validated_data.get("property_offer"),
            deposit_amount=validated_data.get("deposit_amount"),
            deposit_date=deposit_date,
            payment_method=validated_data.get("payment_method"),
            is_additional=True
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.deposit_amount = validated_data.get('deposit_amount', instance.deposit_amount)
        instance.deposit_date = validated_data.get('deposit_date', instance.deposit_date)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(DepositSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class GoodsIncludedSerializer(serializers.ModelSerializer):
    """
    Goods included for a specific offer serializer.
    """

    class Meta:
        model = GoodsIncluded
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = GoodsIncluded.objects.get_or_create(
            property_offer=validated_data.get("property_offer"),
            name=validated_data.get("name")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(GoodsIncludedSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class OfferSerializer(serializers.ModelSerializer):
    """
    Offer for a specific property serializer.
    """

    offer_statuses = OfferStatusSerializer(read_only=True, source="offer_status")
    offer_clients = OfferClientSerializer(many=True, source="property_offer_client")
    offer_agents = OfferAgentSerializer(many=True, required=False, source="property_offer_agent")
    offer_requirements = RequirementSerializer(many=True, required=False, source="property_offer_requirement")
    offer_conditions = ConditionSerializer(many=True, required=False, source="property_offer_condition")
    offer_additional_terms = AdditionalTermSerializer(many=True, required=False,
                                                      source="property_offer_additional_term")
    offer_deposits = DepositSerializer(many=True, required=False, source="property_offer_deposit")
    offer_goods_included = GoodsIncludedSerializer(many=True, required=False, source="property_offer_goods_included")
    offer_additional_documents = OfferAdditionalDocumentsSerializer(many=True, required=False, source="property_offer_additional_documents")
    offer_notes = OfferNoteSerializer(many=True, required=False, source="property_offer_notes")

    class Meta:
        model = Offer
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        property_offer_client = validated_data.pop("property_offer_client", [])
        property_offer_agent = validated_data.pop("property_offer_agent", [])
        property_offer_requirement = validated_data.pop("property_offer_requirement", [])
        property_offer_condition = validated_data.pop("property_offer_condition", [])
        property_offer_additional_term = validated_data.pop("property_offer_additional_term", [])
        property_offer_deposit = validated_data.pop("property_offer_deposit", [])
        property_offer_goods_included = validated_data.pop("property_offer_goods_included", [])
        property_offer_additional_documents = validated_data.pop("property_offer_additional_documents", [])
        property_offer_notes = validated_data.pop("property_offer_notes", [])

        # The default value when deposit date is not provided it should be 3 days from current date of creation.
        default_deposit_date = date.today() + timedelta(days=3)
        default_condition_date = date.today() + timedelta(days=7)
        default_offer_open_till = datetime.now() + timedelta(days=3)

        _created_by = self.context.get("request").user

        instance = Offer(
            connected_property=validated_data.get("connected_property"),
            lead=validated_data.get("lead"),
            offer_status=validated_data.get("offer_status"),
            address=validated_data.get("address"),
            offer_amount=validated_data.get("offer_amount"),
            offer_open_till=validated_data.get("offer_open_till", default_offer_open_till),
            created_by=_created_by,
            representing=validated_data.get("representing"),
            closing_date=validated_data.get("closing_date"),
            property_type=validated_data.get("property_type")
        )

        instance.save()

        if property_offer_client:
            for client in property_offer_client:
                client_payload = {}
                client_phone_number = client.get('phone_number')
                client_email = client.get('email')

                if client_email or client_phone_number:
                    if client.get('email'):
                        client_payload.update({'email': client_email.lower()})
                    if client.get('phone_number'):
                        client_payload.update({'phone_number': client_phone_number})

                    offer_client_instance, _ = OfferClient.objects.get_or_create(
                        property_offer=instance,
                        client=Contact.objects.get_or_create(
                            first_name=client.get('first_name'),
                            last_name=client.get('last_name'),
                            **client_payload
                        )[0],
                        type="Buyer"
                    )

                else:
                    offer_client_instance, _ = OfferClient.objects.get_or_create(
                        property_offer=instance,
                        first_name=client.get('first_name'),
                        last_name=client.get('last_name'),
                        type="Buyer"
                    )

        else:
            raise serializers.ValidationError('Property client is required', code='invalid')

        if _created_by.is_agent:
            offer_agent_instance, _ = OfferAgent.objects.get_or_create(
                property_offer=instance,
                agent=Agent.objects.get(user=_created_by),
                representing=validated_data.get("representing")
            )

        if property_offer_agent:
            for agent in property_offer_agent:
                agent_payload = {}
                if agent.get('email'):
                    agent_payload.update({'email': agent.get('email').lower()})
                if agent.get('phone_number'):
                    agent_payload.update({'phone_number': agent.get('phone_number')})

                offer_agent_instance, _ = OfferAgent.objects.get_or_create(
                    property_offer=instance,
                    agent=Agent.objects.get_or_create(
                        first_name=agent.get('first_name'),
                        last_name=agent.get('last_name'),
                        **agent_payload
                    )[0],
                    representing=agent.get("representing")
                )

        if property_offer_requirement:
            for requirement in property_offer_requirement:
                offer_requirement_instance, _ = Requirement.objects.get_or_create(
                    property_offer=instance,
                    image=requirement.get("image"),
                    note=requirement.get("note")
                )

        if property_offer_condition:
            for condition in property_offer_condition:
                condition_date = condition.get("condition_date") if condition.get("condition_date") else default_condition_date
                offer_condition_instance, _ = Condition.objects.get_or_create(
                    property_offer=instance,
                    name=condition.get("name"),
                    condition_date=condition_date
                )

        if property_offer_additional_term:
            for additional_term in property_offer_additional_term:
                offer_additional_term_instance, _ = AdditionalTerm.objects.get_or_create(
                    property_offer=instance,
                    name=additional_term.get("name")
                )

        if property_offer_deposit:
            for deposit in property_offer_deposit:
                deposit_date = deposit.get("deposit_date") if deposit.get("deposit_date") else default_deposit_date
                offer_deposit_instance, _ = Deposit.objects.get_or_create(
                    property_offer=instance,
                    deposit_amount=deposit.get("deposit_amount"),
                    deposit_date=deposit_date,
                    is_additional=deposit.get('is_additional'),
                    payment_method=deposit.get("payment_method")
                )

        if property_offer_goods_included:
            for goods_included in property_offer_goods_included:
                offer_goods_included_instance, _ = GoodsIncluded.objects.get_or_create(
                    property_offer=instance,
                    name=goods_included.get("name")
                )

        if property_offer_additional_documents:
            for additional_documents in property_offer_additional_documents:
                offer_additional_documents, _ = OfferAdditionalDocuments.objects.get_or_create(
                    property_offer=instance,
                    name=additional_documents.get("name"),
                    created_by=_created_by
                )

        if property_offer_notes:
            for offer_note in property_offer_notes:
                offer_note, _ = OfferNote.objects.get_or_create(
                    property_offer=instance,
                    note=offer_note.get("note"),
                    created_by=_created_by
                )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.connected_property = validated_data.get('connected_property', instance.connected_property)
        instance.lead = validated_data.get('lead', instance.lead)
        instance.address = validated_data.get('address', instance.address)
        instance.offer_amount = validated_data.get('offer_amount', instance.offer_amount)
        instance.offer_open_till = validated_data.get('offer_open_till', instance.offer_open_till)
        instance.offer_status = validated_data.get('offer_status', instance.offer_status)
        instance.representing = validated_data.get('representing', instance.representing)
        instance.closing_date = validated_data.get('closing_date', instance.closing_date)
        instance.is_conveyancing = validated_data.get('is_conveyancing', instance.is_conveyancing)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.property_type = validated_data.get('property_type', instance.property_type)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(OfferSerializer, self).to_representation(instance)
        agents = Agent.objects.filter(offer_agent__property_offer=instance)

        user = self.context.get("request").user
        object_id = OfferNote.objects.filter(property_offer=instance).values_list('id')
        note = UnreadNote.objects.filter(user=user, object_id__in=object_id).order_by('-last_date_viewed').first()
        last_date_viewed = None if not note else TimezoneManager.localize_to_canadian_timezone(note.last_date_viewed)
        unread_count = len(object_id.filter(unread_note=None))

        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
            'created_by': UserProfileSerializer(instance.history.first().history_user).data,
            'offer_agents': AgentSerializer(agents, many=True).data,
            'notes_last_date_viewed': last_date_viewed,
            'unread_notes': unread_count,
        })

        if instance.offer_open_till:
            data.update({
                'offer_open_till': TimezoneManager.localize_to_canadian_timezone(instance.offer_open_till)
            })

        return data

from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.utils import TimezoneManager

from users.serializers import UserProfileSerializer
from .models import (
    Brokerage,
    Agent,
    LawFirm,
    GoodsIncluded,
    Conditions,
    ConditionStatus,
    AdditionalTerms,
    PaymentMethod,
    PropertyType,
    Attachments,
    UnreadNote
)
from contacts.models import (Note as ContactNote)
from leads.models import (Note as LeadNote)
from offers.models import (OfferNote)
from deal.models import (DealNote)


class BrokerageSerializer(serializers.ModelSerializer):
    """
    Component brokerage serializer.
    """

    class Meta:
        model = Brokerage
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = Brokerage.objects.get_or_create(
            name=validated_data.get("name"),
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            fax_number=validated_data.get("fax_number")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.fax_number = validated_data.get('fax_number', instance.fax_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(BrokerageSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class AgentSerializer(serializers.ModelSerializer):
    """
    Component agent serializer.
    """
    agent_brokerage = BrokerageSerializer(read_only=True, source="brokerage")

    class Meta:
        model = Agent
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = Agent.objects.get_or_create(
            user=validated_data.get("user"),
            brokerage=validated_data.get("brokerage"),
            full_name=validated_data.get("full_name"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            fax_number=validated_data.get("fax_number")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.user = validated_data.get('user', instance.user)
        instance.brokerage = validated_data.get('brokerage', instance.brokerage)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.fax_number = validated_data.get('fax_number', instance.fax_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(AgentSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class LawFirmSerializer(serializers.ModelSerializer):
    """
    Component law firm serializer.
    """

    class Meta:
        model = LawFirm
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        instance, _ = LawFirm.objects.get_or_create(
            lawyer_name=validated_data.get("lawyer_name"),
            name=validated_data.get("name"),
            address=validated_data.get("address"),
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            fax_number=validated_data.get("fax_number")
        )

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.lawyer_name = validated_data.get('lawyer_name', instance.lawyer_name)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.fax_number = validated_data.get('fax_number', instance.fax_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(LawFirmSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class GoodsIncludedSerializer(serializers.ModelSerializer):
    """
    Components Goods Included Serializers.
    """

    class Meta:
        model = GoodsIncluded
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = GoodsIncluded.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
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


class ConditionsSerializer(serializers.ModelSerializer):
    """
    Components Conditions Serializers.
    """

    class Meta:
        model = Conditions
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = Conditions.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(ConditionsSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ConditionStatusSerializer(serializers.ModelSerializer):
    """
    Components Condition Status Serializers.
    """

    class Meta:
        model = ConditionStatus
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = ConditionStatus.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(ConditionStatusSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class AdditionalTermsSerializer(serializers.ModelSerializer):
    """
    Components Additional Terms Serializers.
    """

    class Meta:
        model = AdditionalTerms
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = AdditionalTerms.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(AdditionalTermsSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Components Payment Method Serializers.
    """

    class Meta:
        model = PaymentMethod
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = PaymentMethod.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(PaymentMethodSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class PropertyTypeSerializer(serializers.ModelSerializer):
    """
    Components Property Type Serializers.
    """

    class Meta:
        model = PropertyType
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = PropertyType.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(PropertyTypeSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class AttachmentsSerializer(serializers.ModelSerializer):
    """
    Components Attachments Serializers.
    """

    class Meta:
        model = Attachments
        fields = '__all__'

    @transaction.atomic()
    def create(self, validate_data):
        instance, _ = Attachments.objects.get_or_create(**validate_data)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.index = validated_data.get('index', instance.index)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(AttachmentsSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class UnreadNoteSerializer(serializers.ModelSerializer):
    """
    Components Unread Note Serializers.
    """
    user = UserProfileSerializer(read_only=True, required=False)
    content_type = serializers.CharField(required=False)
    object_id = serializers.IntegerField(required=False)
    id = serializers.IntegerField(write_only=True, required=True)
    type = serializers.ChoiceField(write_only=True, choices=['contact', 'lead', 'offer', 'deal'], required=True)

    class Meta:
        model = UnreadNote
        fields = '__all__'

    @transaction.atomic()
    def create(self, validated_data):
        user = self.context.get("request").user
        last_date_viewed = timezone.now()
        content_object = None
        note = None

        if validated_data.get("type") == 'contact':
            try:
                content_object = ContactNote.objects.get(id=validated_data.get('id'))
            except ContactNote.DoesNotExist:
                raise ValidationError({"id": "Invalid note id."})
        if validated_data.get("type") == 'lead':
            try:
                content_object = LeadNote.objects.get(id=validated_data.get('id'))
            except LeadNote.DoesNotExist:
                raise ValidationError({"id": "Invalid note id."})
        if validated_data.get("type") == 'offer':
            try:
                content_object = OfferNote.objects.get(id=validated_data.get('id'))
            except OfferNote.DoesNotExist:
                raise ValidationError({"id": "Invalid note id."})
        if validated_data.get("type") == 'deal':
            try:
                content_object = DealNote.objects.get(id=validated_data.get('id'))
            except DealNote.DoesNotExist:
                raise ValidationError({"id": "Invalid note id."})

        if content_object:
            note = content_object.unread_note.all()

        if not note:
            instance = UnreadNote.objects.create(
                user=user,
                last_date_viewed=last_date_viewed,
                content_object=content_object
            )
        else:
            note[0].last_date_viewed = last_date_viewed
            note[0].save()
            instance = note[0]

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance.last_date_viewed = validated_data.get('last_date_viewed', instance.last_date_viewed)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(UnreadNoteSerializer, self).to_representation(instance)
        data.update({
            'id': instance.id,
            'last_date_viewed': TimezoneManager.localize_to_canadian_timezone(instance.last_date_viewed),
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data

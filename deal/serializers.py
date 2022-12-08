from django.db import transaction
from rest_framework import serializers
from core.utils import TimezoneManager
from contacts.serializers import ContactSerializer
from users.serializers import UserProfileSerializer

from components.serializers import (
    AgentSerializer,
    BrokerageSerializer,
    LawFirmSerializer
)

from deal.models import (
    AdditionalTerm as DealAdditionalTerm,
    Brokerage as DealBrokerage,
    Client as DealClient,
    Commission,
    Condition as DealCondition,
    Deal,
    DealStatus,
    Deposit as DealDeposit,
    GoodsIncluded as DealGoodsIncluded,
    Realtor as DealRealtor,
    LawFirm as DealLawFirm,
    DealAdditionalDocument,
    DealNote
)
from components.models import UnreadNote


class AdditionalTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealAdditionalTerm
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealAdditionalTerm.objects.get_or_create(
            name=validated_data.get('name'),
            note=validated_data.get('note'),
            deal=validated_data.get('deal'),
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.note = validated_data.get('note', instance.note)
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


class DealBrokerageSerializer(serializers.ModelSerializer):
    deal_brokerage = BrokerageSerializer(read_only=True, source='brokerage')

    class Meta:
        model = DealBrokerage
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealBrokerage.objects.get_or_create(
            representing=validated_data.get('representing'),
            brokerage=validated_data.get('brokerage'),
            deal=validated_data.get('deal'),
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.representing = validated_data.get('representing', instance.representing)
        instance.brokerage = validated_data.get('brokerage', instance.brokerage)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(DealBrokerageSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class DealClientSerializer(serializers.ModelSerializer):
    deal_client = ContactSerializer(read_only=True, source="client")

    class Meta:
        model = DealClient
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealClient.objects.get_or_create(
            deal=validated_data.get('deal'),
            client=validated_data.get('client'),
            client_type=validated_data.get('client_type')
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.client_type = validated_data.get('client_type', instance.client_type)
        instance.client = validated_data.get('client', instance.client)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(DealClientSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class CommissionSerializer(serializers.ModelSerializer):
    commission_agent = AgentSerializer(read_only=True, source='agent')

    class Meta:
        model = Commission
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = Commission.objects.get_or_create(
            percentage=validated_data.get('percentage'),
            value_dollars=validated_data.get('value_dollars'),
            GST=validated_data.get('GST'),
            total=validated_data.get('total'),
            notes=validated_data.get('notes'),
            type=validated_data.get('type'),
            agent=validated_data.get('agent'),
            deal=validated_data.get('deal'),
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.percentage = validated_data.get('percentage', instance.percentage)
        instance.value_dollars = validated_data.get('value_dollars', instance.value_dollars)
        instance.GST = validated_data.get('GST', instance.GST)
        instance.total = validated_data.get('total', instance.total)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.type = validated_data.get('total', instance.type)
        instance.agent = validated_data.get('agent', instance.agent)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(CommissionSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealCondition
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealCondition.objects.get_or_create(
            name=validated_data.get('name'),
            status=validated_data.get('status'),
            date=validated_data.get('date'),
            deal=validated_data.get('deal'),
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.date = validated_data.get('date', instance.date)
        instance.status = validated_data.get('status', instance.status)

        _status = validated_data.get('status')

        if _status and _status == 'Waived':
            _status_instance = DealStatus.objects.get(name="Firm Sale")
            instance.deal.status = _status_instance

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

        return data


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealDeposit
        fields = '__all__'

    def validated_is_additional(self, is_additional):
        """
        Validate that there should only be one is_additional=True on every deals.
        """
        if is_additional:
            try:
                _deposit = DealDeposit.objects.get(
                    is_additional=is_additional,
                    deal=self.initial_data.get('deal')
                )
                if _deposit:
                    raise serializers.ValidationError("There is already an additional.")
            except DealDeposit.DoesNotExist:
                pass
            except DealDeposit.MultipleObjectsReturned:
                raise serializers.ValidationError("Multiple Value Returned")
        else:
            is_boolean = isinstance(is_additional, bool)
            if not is_boolean:
                raise serializers.ValidationError("Invalid datatype for is_additional.")

        return is_additional

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealDeposit.objects.get_or_create(
            amount=validated_data.get('amount'),
            date=validated_data.get('date'),
            payment_method=validated_data.get('payment_method'),
            is_additional=validated_data.get('is_additional'),
            deal=validated_data.get('deal')
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.date = validated_data.get('date', instance.date)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.is_additional = validated_data.get('is_additional', instance.is_additional)
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


class RealtorSerializer(serializers.ModelSerializer):
    deal_agent = AgentSerializer(read_only=True, source='agent')

    class Meta:
        model = DealRealtor
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealRealtor.objects.get_or_create(
            representing=validated_data.get('representing'),
            agent=validated_data.get('agent'),
            deal=validated_data.get('deal')
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.representing = validated_data.get('representing', instance.representing)
        instance.agent = validated_data.get('agent', instance.agent)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(RealtorSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class DealLawFirmSerializer(serializers.ModelSerializer):
    deal_law_firm = LawFirmSerializer(read_only=True, source='lawfirm')

    class Meta:
        model = DealLawFirm
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealLawFirm.objects.get_or_create(
            representing=validated_data.get('representing'),
            lawfirm=validated_data.get('lawfirm'),
            deal=validated_data.get('deal'),
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.representing = validated_data.get('representing', instance.representing)
        instance.lawfirm = validated_data.get('lawfirm', instance.lawfirm)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(DealLawFirmSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data


class GoodsIncludedSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealGoodsIncluded
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealGoodsIncluded.objects.get_or_create(
            name=validated_data.get('name'),
            deal=validated_data.get('deal')
        )

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.deal = validated_data.get('deal', instance.deal)
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


class DealNoteSerializer(serializers.ModelSerializer):
    """
    Note for deals.
    """

    class Meta:
        model = DealNote
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        validated_data.update({
            'created_by': self.context.get("request").user
        })
        instance, _ = DealNote.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.deal = validated_data.get('deal', instance.deal)
        instance.note = validated_data.get('note', instance.note)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(DealNoteSerializer, self).to_representation(instance)
        data.update({
            'created_by': UserProfileSerializer(instance.created_by).data
        })

        return data


class DealAdditionalDocumentSerializer(serializers.ModelSerializer):
    """
    Additional document for deals.
    """

    class Meta:
        model = DealAdditionalDocument
        exclude = ['date_created', 'date_updated']

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealAdditionalDocument.objects.get_or_create(**validated_data)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.deal = validated_data.get('deal', instance.deal)
        instance.name = validated_data.get('name', instance.name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance


class BuyerSerializer(serializers.Serializer):
    clients = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    realtors = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    brokerages = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    law_firms = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)


class SellerSerializer(serializers.Serializer):
    clients = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    realtors = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    brokerages = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    law_firms = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)


class ListingCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = '__all__'


class SellingCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = '__all__'


class DealSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False)
    created_by = serializers.CharField(required=False)
    conditions = ConditionSerializer(many=True, source="deal_conditions")
    additional_terms = AdditionalTermSerializer(many=True, source="deal_additional_terms")
    deposits = DepositSerializer(many=True, source="deal_deposit")
    additional_documents = DealAdditionalDocumentSerializer(many=True, required=False,
                                                            source="deal_additional_document")
    notes = DealNoteSerializer(many=True, required=False, source="deal_note")

    # Write Only Fields
    buyer_details = BuyerSerializer(write_only=True)
    seller_details = SellerSerializer(write_only=True)
    selling_commission = SellingCommissionSerializer(many=True, write_only=True)
    listing_commission = ListingCommissionSerializer(many=True, write_only=True)
    goods_included = serializers.ListField(child=serializers.CharField(), write_only=True)

    # Read Only Fields
    clients = DealClientSerializer(many=True, read_only=True, source="client_set")
    realtors = RealtorSerializer(many=True, read_only=True, source="realtor_set")
    brokerages = DealBrokerageSerializer(many=True, read_only=True, source="brokerage_set")
    law_firms = DealLawFirmSerializer(many=True, read_only=True, source="lawfirm_set")
    commissions = CommissionSerializer(many=True, read_only=True, source="commission_set")
    included_goods = GoodsIncludedSerializer(many=True, read_only=True, source="goodsincluded_set")
    is_conditional = serializers.SerializerMethodField()

    class Meta:
        model = Deal
        fields = '__all__'

    def validate_status(self, status):
        status_instance = None
        if status:
            try:
                status_instance = DealStatus.objects.get(name=status)
            except DealStatus.DoesNotExist:
                raise serializers.ValidationError("Invalid Deal Status")

        # If deal has conditions automatically tag deal status to Conditional Sale.
        # TODO: Validate Conditions if status is waived or not.
        if self.initial_data.get('conditions'):
            status_instance = DealStatus.objects.get(name='Conditional Sale')

        return status_instance

    @transaction.atomic
    def create(self, validated_data):
        # Required Fields
        possession_date = validated_data.get('possession_date')
        is_conveyancing = validated_data.get('is_conveyancing')
        representing = validated_data.get('representing')
        sale_price = validated_data.get('sale_price')
        sale_date = validated_data.get('sale_date')
        status = validated_data.get('status')
        property_type = validated_data.get("property_type")

        # Optional Fields
        address = validated_data.get('address')
        connected_property = validated_data.get('connected_property')
        connected_offer = validated_data.get('connected_offer')

        # Foreign Key Connection
        deal_conditions = validated_data.get('deal_conditions')
        deal_additional_terms = validated_data.get('deal_additional_terms')
        deal_deposit = validated_data.get('deal_deposit')
        buyer_details = validated_data.get('buyer_details')
        seller_details = validated_data.get('seller_details')
        listing_commission = validated_data.get('listing_commission')
        selling_commission = validated_data.get('selling_commission')
        goods_included = validated_data.get('goods_included')
        deal_additional_documents = validated_data.get("deal_additional_document")
        deal_notes = validated_data.get("deal_note")

        created_by = self.context.get('request').user

        deal_payload = {
            'possession_date': possession_date,
            'is_conveyancing': is_conveyancing,
            'representing': representing,
            'sale_price': sale_price,
            'sale_date': sale_date,
            'created_by': created_by,
            'status': status,
            'property_type': property_type
        }

        if address:
            deal_payload.update({'address': address})

        if connected_property:
            deal_payload.update({'connected_property': connected_property})

        if connected_offer:
            deal_payload.update({'connected_offer': connected_offer})

        deal_instance = Deal(**deal_payload)
        deal_instance.save()

        if buyer_details:
            clients = buyer_details.get('clients')
            realtors = buyer_details.get('realtors')
            brokerages = buyer_details.get('brokerages')
            law_firms = buyer_details.get('law_firms')

            if clients:
                for _client in clients:
                    DealClient.objects.get_or_create(
                        client_id=_client,
                        deal=deal_instance,
                        client_type='Buy'
                    )

            if realtors:
                for _realtor in realtors:
                    DealRealtor.objects.get_or_create(
                        agent_id=_realtor,
                        deal=deal_instance,
                        representing='Buy'
                    )

            if brokerages:
                for _brokerage in brokerages:
                    DealBrokerage.objects.get_or_create(
                        brokerage_id=_brokerage,
                        deal=deal_instance,
                        representing='Buy'
                    )

            if law_firms:
                for _law_firms in law_firms:
                    DealLawFirm.objects.get_or_create(
                        lawfirm_id=_law_firms,
                        deal=deal_instance,
                        representing='Buy'
                    )

        if seller_details:
            clients = seller_details.get('clients')
            realtors = seller_details.get('realtors')
            brokerages = seller_details.get('brokerages')
            law_firms = seller_details.get('law_firms')

            if clients:
                for _client in clients:
                    DealClient.objects.get_or_create(
                        client_id=_client,
                        deal=deal_instance,
                        client_type='Sell'
                    )

            if realtors:
                for _realtor in realtors:
                    DealRealtor.objects.get_or_create(
                        agent_id=_realtor,
                        deal=deal_instance,
                        representing='Sell'
                    )

            if brokerages:
                for _brokerage in brokerages:
                    DealBrokerage.objects.get_or_create(
                        brokerage_id=_brokerage,
                        deal=deal_instance,
                        representing='Sell'
                    )

            if law_firms:
                for _law_firms in law_firms:
                    DealLawFirm.objects.get_or_create(
                        lawfirm_id=_law_firms,
                        deal=deal_instance,
                        representing='Sell'
                    )

        if deal_conditions:
            for condition in deal_conditions:
                _condition_instance, _ = DealCondition.objects.get_or_create(**condition, deal=deal_instance)

        if deal_additional_terms:
            for _additional_term in deal_additional_terms:
                _additional_term_instance, _ = DealAdditionalTerm.objects.get_or_create(**_additional_term,
                                                                                        deal=deal_instance)

        if deal_deposit:
            for _deposit in deal_deposit:
                _deposit_instance, _ = DealDeposit.objects.get_or_create(**_deposit, deal=deal_instance)

        if selling_commission:
            for commission in selling_commission:
                _selling_commission_instance, _ = Commission.objects.get_or_create(**commission,
                                                                                   deal=deal_instance,
                                                                                   type="Selling")

        if listing_commission:
            for commission in listing_commission:
                _listing_commission_instance, _ = Commission.objects.get_or_create(**commission,
                                                                                   deal=deal_instance,
                                                                                   type="Listing")

        if goods_included:
            for _goods_included in goods_included:
                _goods_included_instance, _ = DealGoodsIncluded.objects.get_or_create(
                    name=_goods_included,
                    deal=deal_instance
                )

        if deal_additional_documents:
            for _additional_document in deal_additional_documents:
                _additional_document_instance, _ = DealAdditionalDocument.objects.get_or_create(
                    name=_additional_document.get("name"),
                    deal=deal_instance
                )

        if deal_notes:
            for _note in deal_notes:
                _note_instance, _ = DealNote.objects.get_or_create(
                    note=_note.get("note"),
                    created_by=created_by,
                    deal=deal_instance
                )

        return deal_instance

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.possession_date = validated_data.get('possession_date', instance.possession_date)
        instance.is_conveyancing = validated_data.get('is_conveyancing', instance.is_conveyancing)
        instance.representing = validated_data.get('representing', instance.representing)
        instance.sale_price = validated_data.get('sale_price', instance.sale_price)
        instance.sale_date = validated_data.get('sale_date', instance.sale_date)
        instance.address = validated_data.get('address', instance.address)
        instance.status = validated_data.get('status', instance.status)
        instance.property_type = validated_data.get('property_type', instance.property_type)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        return instance

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(DealSerializer, self).to_representation(instance)

        user = self.context.get("request").user
        object_id = DealNote.objects.filter(deal=instance).values_list('id')
        note = UnreadNote.objects.filter(user=user, object_id__in=object_id).order_by('-last_date_viewed').first()
        last_date_viewed = None if not note else TimezoneManager.localize_to_canadian_timezone(note.last_date_viewed)
        unread_count = len(object_id.filter(unread_note=None))

        data.update({
            'possession_date': TimezoneManager.localize_to_canadian_timezone(instance.possession_date),
            'sale_date': TimezoneManager.localize_to_canadian_timezone(instance.sale_date),
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
            'notes_last_date_viewed': last_date_viewed,
            'unread_notes': unread_count,
        })

        return data

    @staticmethod
    def get_is_conditional(obj):
        if obj.deal_conditions.filter(is_active=True, status__in=['Waiting', 'Not Waived']).count():
            return True
        return False


class DealStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealStatus
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        instance, _ = DealStatus.objects.get_or_create(name=validated_data.get('name'))

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
        data = super(DealStatusSerializer, self).to_representation(instance)
        data.update({
            'date_created': TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated),
        })

        return data

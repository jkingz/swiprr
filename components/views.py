import json

from rest_framework import viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

from core.mixins import DestroyArchiveModelMixin, HomeswiprCreateModelMixin

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

from .serializers import (
    BrokerageSerializer,
    AgentSerializer,
    LawFirmSerializer,
    GoodsIncludedSerializer,
    ConditionsSerializer,
    ConditionStatusSerializer,
    AdditionalTermsSerializer,
    PaymentMethodSerializer,
    PropertyTypeSerializer,
    AttachmentsSerializer,
    UnreadNoteSerializer
)


class BrokerageViewSet(viewsets.GenericViewSet,
                       HomeswiprCreateModelMixin,
                       UpdateModelMixin,
                       DestroyArchiveModelMixin):
    """
    Component brokerage view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = BrokerageSerializer
    queryset = Brokerage.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Brokerage.objects.all().order_by('-id')
        brokerage = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(brokerage)
        response = Response(serializer.data)

        return response


class AgentViewSet(viewsets.GenericViewSet,
                   HomeswiprCreateModelMixin,
                   UpdateModelMixin,
                   DestroyArchiveModelMixin):
    """
    Component agent view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AgentSerializer

    def get_queryset(self, *args, **kwargs):
        agent_payload = {'is_active': True}
        user = self.request.query_params.get('with_user_account', "")
        agents = self.request.query_params.get('agents', "")
        search_text = self.request.query_params.get('search_text', "")

        if user and bool(user) is True:
            agent_payload.update({'user__isnull': False})
        if agents:
            agent_payload.update({'id__in': json.loads(agents)})

        agents = Agent.objects.filter(**agent_payload)

        if search_text:
            agents = Agent.objects.filter(
                Q(first_name__icontains=search_text) |
                Q(last_name__icontains=search_text) |
                Q(full_name__icontains=search_text) |
                Q(phone_number__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(fax_number__icontains=search_text) |
                Q(brokerage__name__icontains=search_text) |
                Q(brokerage__email__icontains=search_text) |
                Q(brokerage__phone_number__icontains=search_text) |
                Q(brokerage__fax_number__icontains=search_text),
                **agent_payload
            )

        return agents.order_by('id').distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Agent.objects.all().order_by('-id')
        agent = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(agent)
        response = Response(serializer.data)

        return response


class LawFirmViewSet(viewsets.GenericViewSet,
                     HomeswiprCreateModelMixin,
                     UpdateModelMixin,
                     DestroyArchiveModelMixin):
    """
    Component law firm app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LawFirmSerializer
    queryset = LawFirm.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = LawFirm.objects.all().order_by('-id')
        law_firm = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(law_firm)
        response = Response(serializer.data)

        return response


class GoodsIncludedViewSet(viewsets.GenericViewSet,
                           HomeswiprCreateModelMixin,
                           UpdateModelMixin,
                           DestroyArchiveModelMixin):
    """
    Component Goods Included app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = GoodsIncludedSerializer
    queryset = GoodsIncluded.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = GoodsIncluded.objects.all().order_by('-id')
        goods_included = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(goods_included)
        response = Response(serializer.data)

        return response


class ConditionViewSet(viewsets.GenericViewSet,
                       HomeswiprCreateModelMixin,
                       UpdateModelMixin,
                       DestroyArchiveModelMixin):
    """
    Component Condition app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ConditionsSerializer
    queryset = Conditions.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Conditions.objects.all().order_by('-id')
        condition = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(condition)
        response = Response(serializer.data)

        return response


class ConditionStatusViewSet(viewsets.GenericViewSet,
                             HomeswiprCreateModelMixin,
                             UpdateModelMixin,
                             DestroyArchiveModelMixin):
    """
    Component Condition Status app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ConditionStatusSerializer
    queryset = ConditionStatus.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = ConditionStatus.objects.all().order_by('-id')
        condition_status = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(condition_status)
        response = Response(serializer.data)

        return response


class AdditionalTermsViewSet(viewsets.GenericViewSet,
                             HomeswiprCreateModelMixin,
                             UpdateModelMixin,
                             DestroyArchiveModelMixin):
    """
    Component Additional Terms app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AdditionalTermsSerializer
    queryset = AdditionalTerms.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = AdditionalTerms.objects.all().order_by('-id')
        additional_term = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(additional_term)
        response = Response(serializer.data)

        return response


class PaymentMethodViewSet(viewsets.GenericViewSet,
                           HomeswiprCreateModelMixin,
                           UpdateModelMixin,
                           DestroyArchiveModelMixin):
    """
    Component Payment Method app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentMethodSerializer
    queryset = PaymentMethod.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = PaymentMethod.objects.all().order_by('-id')
        payment_method = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(payment_method)
        response = Response(serializer.data)

        return response


class PropertyTypeViewSet(viewsets.GenericViewSet,
                          HomeswiprCreateModelMixin,
                          UpdateModelMixin,
                          DestroyArchiveModelMixin):
    """
    Component Property Type app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PropertyTypeSerializer
    queryset = PropertyType.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = PropertyType.objects.all().order_by('-id')
        property_type = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(property_type)
        response = Response(serializer.data)

        return response


class AttachmentsViewSet(viewsets.GenericViewSet,
                         HomeswiprCreateModelMixin,
                         UpdateModelMixin,
                         DestroyArchiveModelMixin):
    """
    Component Attachments app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentsSerializer
    queryset = Attachments.active_objects.filter(is_active=True).order_by('index')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Attachments.objects.all().order_by('-id')
        attachment = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(attachment)
        response = Response(serializer.data)

        return response


class UnreadNoteViewSet(viewsets.GenericViewSet,
                        HomeswiprCreateModelMixin,
                        UpdateModelMixin,
                        DestroyArchiveModelMixin):
    """
    Component Unread Note app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UnreadNoteSerializer
    queryset = UnreadNote.objects.all().order_by('-last_date_viewed')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = UnreadNote.objects.all()
        attachment = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(attachment)
        response = Response(serializer.data)

        return response

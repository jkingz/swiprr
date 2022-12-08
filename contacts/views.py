import json

from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from core.mixins import HomeswiprCreateModelMixin, DestroyArchiveModelMixin
from core.pagination import LargeResultsSetPagination
from core.utils import CaseInsensitiveOrderingFilter
from core.permissions import IsMortgageBroker, IsAgentUser, IsAdmin

from contacts.models import (
    Contact,
    ContactAgent,
    Note,
    ContactMortgageBroker,
    ContactSalesAgent
)
from contacts.serializers import (
    ContactSerializer,
    ContactAgentSerializer,
    ContactNoteSerializer,
    ContactMortgageBrokerSerializer,
    ContactSalesAgentSerializer
)


class ContactViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    """
    Contact app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ContactSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [CaseInsensitiveOrderingFilter]
    ordering_fields = [
        'id',
        'phone_number',
        'email',
        'source',
        'city',
        'occupation',
        'associated_company',
        'date_created',
        'date_updated',
    ]
    ordering = '-id'

    def get_queryset(self, *args, **kwargs):
        _excluded_id = []
        contact_payload = {'is_active': True}
        agents = self.request.query_params.get("agents", "")
        mortgage_brokers = self.request.query_params.get("mortgage_brokers", "")
        sales_agents = self.request.query_params.get("sales_agents", "")
        search_text = self.request.query_params.get("search_text", "")
        has_lead = self.request.query_params.get("has_lead", "")
        contact_ids = self.request.query_params.get("contact_ids", "")
        is_archived = self.request.query_params.get('is_archived', "")
        with_agents = self.request.query_params.get('with_agents', "")
        with_sales_agents = self.request.query_params.get('with_sales_agents', "")
        with_mortgage_brokers = self.request.query_params.get('with_mortgage_brokers', "")

        if is_archived and is_archived == 'True':
            contact_payload.update({'is_active': False})
        if with_agents and with_agents == 'True':
            contact_payload.update({'contact_agent__isnull': False})
        elif with_agents and with_agents == 'False':
            contact_payload.update({'contact_agent__isnull': True})
        if with_sales_agents and with_sales_agents == 'True':
            contact_payload.update({'contact_sales_agent__isnull': False})
        elif with_sales_agents and with_sales_agents == 'False':
            contact_payload.update({'contact_sales_agent__isnull': True})
        if with_mortgage_brokers and with_mortgage_brokers == 'True':
            contact_payload.update({'contact_mortgage_broker__isnull': False})
        elif with_mortgage_brokers and with_mortgage_brokers == 'False':
            contact_payload.update({'contact_mortgage_broker__isnull': True})
        if contact_ids:
            contact_payload.update({'id__in': json.loads(contact_ids)})
        if agents:
            contact_payload.update({'contact_agent__agent__id__in': json.loads(agents)})
        if mortgage_brokers:
            contact_payload.update({'contact_mortgage_broker__mortgage_broker__id__in': json.loads(mortgage_brokers)})
        if sales_agents:
            contact_payload.update({'contact_sales_agent__sales_agent__id__in': json.loads(sales_agents)})

        contacts = Contact.objects.filter(**contact_payload)

        if search_text:
            contacts = Contact.objects.filter(
                Q(first_name__icontains=search_text) |
                Q(last_name__icontains=search_text) |
                Q(middle_name__icontains=search_text) |
                Q(phone_number__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(city__icontains=search_text) |
                Q(associated_company__icontains=search_text) |
                Q(occupation__icontains=search_text) |
                Q(source__icontains=search_text) |
                Q(contact_note__note__icontains=search_text),
                **contact_payload
            )

        if has_lead:
            for _contact in contacts:
                if has_lead == 'True':
                    if _contact.has_lead is False:
                        _excluded_id.append(_contact.id)
                if has_lead == 'False':
                    if _contact.has_lead is True:
                        _excluded_id.append(_contact.id)

        if agents:
            if len(json.loads(agents)) > 1:
                for _contact in contacts:
                    for _agent in _contact.contact_agent.all():
                        if _agent.agent.id not in json.loads(agents) or \
                                len(_contact.contact_agent.all()) != len(json.loads(agents)):
                            _excluded_id.append(_contact.id)

        if mortgage_brokers:
            if len(json.loads(mortgage_brokers)) > 1:
                for _contact in contacts:
                    for _mortgage_broker in _contact.contact_mortgage_broker.all():
                        if _mortgage_broker.mortgage_broker.id not in json.loads(mortgage_brokers) or \
                                len(_contact.contact_mortgage_broker.all()) != len(json.loads(mortgage_brokers)):
                            _excluded_id.append(_contact.id)

        if sales_agents:
            if len(json.loads(sales_agents)) > 1:
                for _contact in contacts:
                    for _sales_agent in _contact.contact_sales_agent.all():
                        if _sales_agent.sales_agent.id not in json.loads(sales_agents) or \
                                len(_contact.contact_sales_agent.all()) != len(json.loads(sales_agents)):
                            _excluded_id.append(_contact.id)

        return contacts.exclude(id__in=_excluded_id).distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        user = self.request.user

        if user.is_user_manager or user.is_superuser:
            queryset = queryset

        elif user.is_agent:
            queryset = queryset.filter(contact_agent__agent__user__id=user.id)

        elif user.user_type and user.user_type.type == 'Mortgage Broker':
            queryset = queryset.filter(contact_mortgage_broker__mortgage_broker__id=user.id)

        elif user.user_type and user.user_type.type == 'Sales Agent':
            queryset = queryset.filter(contact_sales_agent__sales_agent__id=user.id)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        contact = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(contact)
        response = Response(serializer.data)

        return response


class ContactAgentViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    """
    Contact agent app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ContactAgentSerializer
    queryset = ContactAgent.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = ContactAgent.objects.all().order_by('-id')
        offer_agent = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_agent)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_contact_agent(self, *args, **kwargs):
        agent_id = self.request.data.get('agent')
        contact_id = self.request.data.get('contact')
        if agent_id and contact_id:
            try:
                contact_agent = ContactAgent.objects.get(agent__id=int(agent_id), contact__id=int(contact_id))
                contact_agent.delete()
            except ContactAgent.DoesNotExist:
                return Response(
                    {"detail": "Invalid Params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Invalid Params"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Successfully deleted!"}, status=status.HTTP_200_OK)


class ContactNoteViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    """
    Contact note app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ContactNoteSerializer

    def get_queryset(self, *args, **kwargs):
        note_payload = {'is_active': True}
        contact = self.request.query_params.get("contact", "")

        if contact:
            note_payload.update({'contact__id': int(contact)})

        notes = Note.objects.filter(**note_payload)

        return notes.order_by('-id').distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Note.objects.all().order_by('-id')
        offer_agent = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_agent)
        response = Response(serializer.data)

        return response


class ContactMortgageBrokerViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):

    """
    Contact note app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ContactMortgageBrokerSerializer
    queryset = ContactMortgageBroker.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = ContactMortgageBroker.objects.all().order_by('-id')
        mortgage_broker = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(mortgage_broker)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_contact_mortgage_broker(self, *args, **kwargs):
        mortgage_broker_id = self.request.query_params.get('mortgage_broker')

        if mortgage_broker_id:
            try:
                mortgage_broker = ContactMortgageBroker.objects.get(id=int(mortgage_broker_id))
                mortgage_broker.delete()
            except ContactMortgageBroker.DoesNotExist:
                return Response(
                    {"detail": "Invalid Params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Invalid Params"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Successfully deleted!"}, status=status.HTTP_200_OK)


class ContactSalesAgentViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):

    """
    Contact note app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ContactSalesAgentSerializer
    queryset = ContactSalesAgent.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = ContactSalesAgent.objects.all().order_by('-id')
        sales_agent = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(sales_agent)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_contact_sales_agent(self, *args, **kwargs):
        sales_agent_id = self.request.query_params.get('sales_agent')

        if sales_agent_id:
            try:
                sales_agent = ContactSalesAgent.objects.get(id=int(sales_agent_id))
                sales_agent.delete()
            except ContactSalesAgent.DoesNotExist:
                return Response(
                    {"detail": "Invalid Params"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Invalid Params"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Successfully deleted!"}, status=status.HTTP_200_OK)

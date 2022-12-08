import json

from core.pagination import LargeResultsSetPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from core.mixins import HomeswiprCreateModelMixin, DestroyArchiveModelMixin
from core.utils import CaseInsensitiveOrderingFilter

from leads.models import (
    Lead,
    LeadContact,
    LeadAgents,
    LeadStatus,
    Note,
    FinancialStatus,
    ContactType,
    LeadWarmth,
    TimeFrame,
    LeadMortgageBroker,
    LeadSalesAgent
)
from leads.serializers import (
    LeadSerializer,
    LeadStatusSerializer,
    LeadAgentsSerializer,
    LeadContactSerializer,
    NoteSerializer,
    FinancialStatusSerializer,
    ContactTypeSerializer,
    LeadWarmthSerializer,
    TimeFrameSerializer,
    LeadMortgageBrokerSerializer,
    LeadSalesAgentSerializer
)


class LeadViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = [CaseInsensitiveOrderingFilter]
    ordering_fields = [
        'id',
        'contact_type__name',
        'lead_warmth__index',
        'lead_status__name',
        'financial_status__name',
        'client_criteria',
        'transaction_type',
        'time_frame__range',
        'is_flag',
        'date_created',
        'date_updated',
        'property_address',
        'initial_contact_made',
        'market_report',
        'search_set',
        'offers',
        'deals',
        'cma_created',
        'enroll_in_structurely'
    ]
    ordering = '-id'

    def get_queryset(self, *args, **kwargs):
        lead_payload = {'is_active': True}
        _search_text = self.request.query_params.get('search_text', "")
        _contact_type = self.request.query_params.get('contact_type', "")
        _transaction_type = self.request.query_params.get('transaction_type', "")
        _lead_warmth = self.request.query_params.get("lead_warmth", "")
        _agents = self.request.query_params.get("agents", "")
        _mortgage_brokers = self.request.query_params.get("mortgage_brokers", "")
        _sales_agents = self.request.query_params.get("sales_agents", "")
        _lead_statuses = self.request.query_params.get("lead_statuses", "")
        _contact_id = self.request.query_params.get('contact_id', "")
        _closed_lead = self.request.query_params.get('closed_lead', "")
        _is_flag = self.request.query_params.get('is_flag', "")
        is_archived = self.request.query_params.get('is_archived', "")
        with_agents = self.request.query_params.get('with_agents', "")
        with_sales_agents = self.request.query_params.get('with_sales_agents', "")
        with_mortgage_brokers = self.request.query_params.get('with_mortgage_brokers', "")
        excluded_lead_payload = {'lead_status__name': 'Closed Lead'}
        _excluded_id = []

        if is_archived and is_archived == 'True':
            lead_payload.update({'is_active': False})
        if with_agents and with_agents == 'True':
            lead_payload.update({'leadagents__isnull': False})
        elif with_agents and with_agents == 'False':
            lead_payload.update({'leadagents__isnull': True})
        if with_sales_agents and with_sales_agents == 'True':
            lead_payload.update({'leadsalesagent__isnull': False})
        elif with_sales_agents and with_sales_agents == 'False':
            lead_payload.update({'leadsalesagent__isnull': True})
        if with_mortgage_brokers and with_mortgage_brokers == 'True':
            lead_payload.update({'leadmortgagebroker__isnull': False})
        elif with_mortgage_brokers and with_mortgage_brokers == 'False':
            lead_payload.update({'leadmortgagebroker__isnull': True})
        if _is_flag:
            lead_payload.update({'is_flag': _is_flag})
        if _contact_id:
            lead_payload.update({'leadcontact__contact__id': int(_contact_id)})
        if _contact_type:
            lead_payload.update({'contact_type__name': _contact_type})
        if _transaction_type:
            lead_payload.update({'transaction_type': _transaction_type})
        if _lead_warmth:
            lead_payload.update({'lead_warmth__name': _lead_warmth})
        if _agents:
            lead_payload.update({'leadagents__agent_assigned__id__in': json.loads(_agents)})
        if _mortgage_brokers:
            lead_payload.update({'leadmortgagebroker__mortgage_broker__id__in': json.loads(_mortgage_brokers)})
        if _sales_agents:
            lead_payload.update({'leadsalesagent__sales_agent__id__in': json.loads(_sales_agents)})
        if _lead_statuses:
            lead_payload.update({'lead_status__id__in': json.loads(_lead_statuses)})
        if _closed_lead and _closed_lead == 'True':
            excluded_lead_payload.pop('lead_status__name')
            lead_payload.update({'lead_status__name': 'Closed Lead'})

        leads = Lead.objects.filter(**lead_payload).exclude(**excluded_lead_payload)

        if _search_text:
            leads = Lead.objects.filter(
                Q(financial_status__name__icontains=_search_text) |
                Q(lead_status__name__icontains=_search_text) |
                Q(client_criteria__icontains=_search_text) |
                Q(leadcontact__contact__first_name__icontains=_search_text) |
                Q(leadcontact__contact__last_name__icontains=_search_text) |
                Q(leadcontact__contact__email__icontains=_search_text) |
                Q(leadcontact__contact__phone_number__icontains=_search_text) |
                Q(leadagents__agent_assigned__full_name__icontains=_search_text) |
                Q(leadagents__agent_assigned__first_name__icontains=_search_text) |
                Q(leadagents__agent_assigned__last_name__icontains=_search_text) |
                Q(leadagents__agent_assigned__email__icontains=_search_text) |
                Q(leadagents__agent_assigned__phone_number__icontains=_search_text) |
                Q(lead_warmth__name__icontains=_search_text) |
                Q(time_frame__range__icontains=_search_text) |
                Q(note__note__icontains=_search_text),
                **lead_payload
            ).exclude(**excluded_lead_payload)

        if _agents:
            if len(json.loads(_agents)) > 1:
                for _lead in leads:
                    for _agent in _lead.leadagents_set.all():
                        if _agent.agent_assigned.id not in json.loads(_agents) or \
                                len(_lead.leadagents_set.all()) != len(json.loads(_agents)):
                            _excluded_id.append(_lead.id)

        if _mortgage_brokers:
            if len(json.loads(_mortgage_brokers)) > 1:
                for _lead in leads:
                    for _mortgage_broker in _lead.leadmortgagebroker_set.all():
                        if _mortgage_broker.mortgage_broker.id not in json.loads(_mortgage_brokers) or \
                                len(_lead.leadmortgagebroker_set.all()) != len(json.loads(_mortgage_brokers)):
                            _excluded_id.append(_lead.id)

        if _sales_agents:
            if len(json.loads(_sales_agents)) > 1:
                for _lead in leads:
                    for _sales_agent in _lead.leadsalesagent_set.all():
                        if _sales_agent.sales_agent.id not in json.loads(_sales_agents) or \
                                len(_lead.leadsalesagent_set.all()) != len(json.loads(_sales_agents)):
                            _excluded_id.append(_lead.id)

        return leads.exclude(id__in=_excluded_id).distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        user = self.request.user

        if user.is_user_manager or user.is_superuser:
            queryset = queryset

        elif user.is_agent:
            queryset = queryset.filter(leadagents__agent_assigned__user__id=user.id)

        elif user.user_type and user.user_type.type == 'Mortgage Broker':
            queryset = queryset.filter(leadmortgagebroker__mortgage_broker__id=user.id)

        elif user.user_type and user.user_type.type == 'Sales Agent':
            queryset = queryset.filter(leadsalesagent__sales_agent__id=user.id)

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Lead.objects.all().order_by('id')
        leads = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(leads)
        response = Response(serializer.data)

        return response


class LeadStatusViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadStatusSerializer

    def get_queryset(self, *args, **kwargs):
        lead_status = LeadStatus.active_objects.all()
        return lead_status

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        lead_status = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(lead_status)
        response = Response(serializer.data)
        return response


class LeadAgentsViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadAgentsSerializer

    def get_queryset(self, *args, **kwargs):
        lead_agents = LeadAgents.active_objects.all()
        return lead_agents

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        lead_agents = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(lead_agents)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_agent_lead_connection(self, *args, **kwargs):
        lead_id = self.request.query_params.get('lead_id')
        agent_id = self.request.query_params.get('agent_id')

        if lead_id and agent_id:
            try:
                lead = LeadAgents.objects.get(lead__id=int(lead_id), agent_assigned__id=int(agent_id))
                lead.delete()
            except LeadAgents.DoesNotExist:
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


class LeadContactViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadContactSerializer

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        lead_contacts = LeadContact.active_objects.all()

        _contact_type = self.request.query_params.get('contact_type', None)
        _transaction_type = self.request.query_params.get('transaction_type', None)

        if _contact_type:
            lead_contacts = lead_contacts.filter(lead__contact_type__name=_contact_type)

        if _transaction_type: 
            lead_contacts = lead_contacts.filter(lead__transaction_type=_transaction_type)

        if not user.is_superuser and user.is_agent:
            lead_contacts = lead_contacts.filter(lead__leadagents__agent_assigned__user=user)
        elif not user.is_superuser and user.is_user_manager:
            lead_contacts = lead_contacts.filter(lead__leadagents__agent_assigned__user=user)

        return lead_contacts

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        lead_contacts = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(lead_contacts)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_contact_lead_connection(self, *args, **kwargs):
        lead_id = self.request.query_params.get('lead_id')
        contact_id = self.request.query_params.get('contact_id')

        if lead_id and contact_id:
            try:
                lead = LeadContact.objects.get(lead__id=int(lead_id), contact__id=int(contact_id))
                lead.delete()
            except LeadContact.DoesNotExist:
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


class LeadMortgageBrokerViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadMortgageBrokerSerializer
    queryset = LeadMortgageBroker.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = LeadMortgageBroker.objects.all().order_by('-id')
        mortgage_broker = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(mortgage_broker)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_lead_mortgage_broker(self, *args, **kwargs):
        mortgage_broker_id = self.request.query_params.get('mortgage_broker')

        if mortgage_broker_id:
            try:
                mortgage_broker = LeadMortgageBroker.objects.get(id=int(mortgage_broker_id))
                mortgage_broker.delete()
            except LeadMortgageBroker.DoesNotExist:
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


class LeadSalesAgentViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadSalesAgentSerializer
    queryset = LeadSalesAgent.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = LeadSalesAgent.objects.all().order_by('-id')
        sales_agent = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(sales_agent)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_lead_sales_agent(self, *args, **kwargs):
        sales_agent_id = self.request.query_params.get('sales_agent')

        if sales_agent_id:
            try:
                sales_agent = LeadSalesAgent.objects.get(id=int(sales_agent_id))
                sales_agent.delete()
            except LeadSalesAgent.DoesNotExist:
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


class NoteViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = NoteSerializer

    def get_queryset(self, *args, **kwargs):
        note_payload = {'is_active': True}
        lead = self.request.query_params.get("lead", "")

        if lead:
            note_payload.update({'lead__id': int(lead)})

        notes = Note.objects.filter(**note_payload)

        return notes.order_by('-id').distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Note.objects.all().order_by('-id')
        notes = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(notes)
        response = Response(serializer.data)
        return response


class FinancialStatusViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = FinancialStatusSerializer

    def get_queryset(self, *args, **kwargs):
        notes = FinancialStatus.active_objects.all()
        return notes

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        notes = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(notes)
        response = Response(serializer.data)
        return response


class ContactTypeViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = ContactTypeSerializer

    def get_queryset(self, *args, **kwargs):
        notes = ContactType.active_objects.all()
        return notes

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        notes = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(notes)
        response = Response(serializer.data)
        return response


class LeadWarmthViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = LeadWarmthSerializer

    def get_queryset(self, *args, **kwargs):
        lead_warmth = LeadWarmth.active_objects.all()
        return lead_warmth

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        notes = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(notes)
        response = Response(serializer.data)
        return response


class TimeFrameViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = TimeFrameSerializer

    def get_queryset(self, *args, **kwargs):
        time_frame = TimeFrame.active_objects.all()
        return time_frame

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        notes = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(notes)
        response = Response(serializer.data)
        return response

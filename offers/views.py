import json

from rest_framework import viewsets, status
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from core.pagination import LargeResultsSetPagination
from rest_framework.decorators import action
from core.mixins import DestroyArchiveModelMixin, HomeswiprCreateModelMixin

from .models import (
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
from .serializers import (
    OfferSerializer,
    OfferStatusSerializer,
    OfferClientSerializer,
    OfferAgentSerializer,
    OfferNoteSerializer,
    RequirementSerializer,
    ConditionSerializer,
    AdditionalTermSerializer,
    DepositSerializer,
    GoodsIncludedSerializer,
    OfferAdditionalDocumentsSerializer
)


class OfferStatusViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferStatusSerializer

    def get_queryset(self, *args, **kwargs):
        offer_status = OfferStatus.active_objects.all()

        return offer_status

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        offer_status = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_status)
        response = Response(serializer.data)

        return response


class OfferNoteViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferNoteSerializer

    def get_queryset(self, *args, **kwargs):
        offer_id = self.request.query_params.get('offer', None)
        offer_note = OfferNote.active_objects.all()

        if offer_id:
            offer_note = offer_note.filter(property_offer__id=int(offer_id))

        return offer_note

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        offer_note = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_note)
        response = Response(serializer.data)

        return response


class OfferOfferAdditionalDocumentsViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferAdditionalDocumentsSerializer

    def get_queryset(self, *args, **kwargs):
        offer_id = self.request.query_params.get('offer', None)
        offer_attachment_documents = OfferAdditionalDocuments.active_objects.all()

        if offer_id:
            offer_attachment_documents = offer_attachment_documents.filter(property_offer__id=int(offer_id))

        return offer_attachment_documents

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        offer_attachment_documents = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_attachment_documents)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_additional_document_offer_connection(self, *args, **kwargs):
        additional_document_id = self.request.query_params.get('additional_document_id')

        if additional_document_id:
            try:
                additional_document = OfferAdditionalDocuments.objects.get(id=int(additional_document_id))
                additional_document.delete()
            except OfferAdditionalDocuments.DoesNotExist:
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


class OfferClientViewSet(viewsets.GenericViewSet,
                         HomeswiprCreateModelMixin,
                         UpdateModelMixin,
                         DestroyArchiveModelMixin):
    """
    Offer client app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OfferClientSerializer
    queryset = OfferClient.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = OfferClient.objects.all().order_by('-id')
        offer_client = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_client)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_client_offer_connection(self, *args, **kwargs):
        offer_client_id = self.request.query_params.get('offer_client_id')

        if offer_client_id:
            try:
                offer = OfferClient.objects.get(id=int(offer_client_id))
                offer.delete()
            except OfferClient.DoesNotExist:
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


class OfferAgentViewSet(viewsets.GenericViewSet,
                        HomeswiprCreateModelMixin,
                        UpdateModelMixin,
                        DestroyArchiveModelMixin):
    """
    Offer agent app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OfferAgentSerializer
    queryset = OfferAgent.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = OfferAgent.objects.all().order_by('-id')
        offer_agent = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_agent)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_agent_offer_connection(self, *args, **kwargs):
        offer_id = self.request.query_params.get('offer_id')
        agent_id = self.request.query_params.get('agent_id')

        if offer_id and agent_id:
            try:
                offer = OfferAgent.objects.get(property_offer__id=int(offer_id), agent__id=int(agent_id))
                offer.delete()
            except OfferAgent.DoesNotExist:
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


class RequirementViewSet(viewsets.GenericViewSet,
                         HomeswiprCreateModelMixin,
                         UpdateModelMixin,
                         DestroyArchiveModelMixin):
    """
    Requirement app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = RequirementSerializer
    queryset = Requirement.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Requirement.objects.all().order_by('-id')
        offer_requirement = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_requirement)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_requirement_offer_connection(self, *args, **kwargs):
        requirement_id = self.request.query_params.get('requirement_id')

        if requirement_id:
            try:
                requirement = Requirement.objects.get(id=int(requirement_id))
                requirement.delete()
            except Requirement.DoesNotExist:
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


class ConditionViewSet(viewsets.GenericViewSet,
                       HomeswiprCreateModelMixin,
                       UpdateModelMixin,
                       DestroyArchiveModelMixin):
    """
    Condition app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ConditionSerializer
    queryset = Condition.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Condition.objects.all().order_by('-id')
        offer_condition = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_condition)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_condition_offer_connection(self, *args, **kwargs):
        condition_id = self.request.query_params.get('condition_id')

        if condition_id:
            try:
                condition = Condition.objects.get(id=int(condition_id))
                condition.delete()
            except Condition.DoesNotExist:
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


class AdditionalTermViewSet(viewsets.GenericViewSet,
                            HomeswiprCreateModelMixin,
                            UpdateModelMixin,
                            DestroyArchiveModelMixin):
    """
    Additional term app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AdditionalTermSerializer
    queryset = AdditionalTerm.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = AdditionalTerm.objects.all().order_by('-id')
        offer_additional_term = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_additional_term)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_additional_term_offer_connection(self, *args, **kwargs):
        additional_term_id = self.request.query_params.get('additional_term_id')

        if additional_term_id:
            try:
                additional_term = AdditionalTerm.objects.get(id=int(additional_term_id))
                additional_term.delete()
            except Deposit.DoesNotExist:
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


class DepositViewSet(viewsets.GenericViewSet,
                     HomeswiprCreateModelMixin,
                     UpdateModelMixin,
                     DestroyArchiveModelMixin):
    """
    Deposit app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DepositSerializer
    queryset = Deposit.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Deposit.objects.all().order_by('-id')
        offer_deposit = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_deposit)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_deposit_offer_connection(self, *args, **kwargs):
        deposit_id = self.request.query_params.get('deposit_id')

        if deposit_id:
            try:
                deposit = Deposit.objects.get(id=int(deposit_id))
                deposit.delete()
            except Deposit.DoesNotExist:
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


class GoodsIncludedViewSet(viewsets.GenericViewSet,
                           HomeswiprCreateModelMixin,
                           UpdateModelMixin,
                           DestroyArchiveModelMixin):
    """
    Goods included app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = GoodsIncludedSerializer
    queryset = GoodsIncluded.active_objects.filter(is_active=True).order_by('-id')

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = GoodsIncluded.objects.all().order_by('-id')
        offer_deposit = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer_deposit)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_goods_included_offer_connection(self, *args, **kwargs):
        goods_included_id = self.request.query_params.get('goods_included_id')

        if goods_included_id:
            try:
                goods_included = GoodsIncluded.objects.get(id=int(goods_included_id))
                goods_included.delete()
            except GoodsIncluded.DoesNotExist:
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


class OfferViewSet(viewsets.GenericViewSet,
                   HomeswiprCreateModelMixin,
                   UpdateModelMixin,
                   DestroyArchiveModelMixin):
    """
    Offer app view set.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OfferSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        offer_payload = {'is_active': True}
        is_archived = self.request.query_params.get('is_archived', "")
        agents = self.request.query_params.get("agents", "")
        offer_status = self.request.query_params.get("statuses", "")
        search_text = self.request.query_params.get("search_text", "")

        if is_archived and is_archived == 'True':
            offer_payload.update({'is_active': False})
        if agents:
            offer_payload.update({'property_offer_agent__agent__id__in': json.loads(agents)})
        if offer_status:
            offer_payload.update({'offer_status__name__in': json.loads(offer_status)})

        offers = Offer.objects.filter(**offer_payload)

        if search_text:
            offers = Offer.objects.filter(
                Q(address__icontains=search_text) |
                Q(representing__icontains=search_text) |
                Q(property_offer_client__client__first_name__icontains=search_text) |
                Q(property_offer_client__client__last_name__icontains=search_text) |
                Q(property_offer_client__client__email__icontains=search_text) |
                Q(property_offer_client__client__phone_number__icontains=search_text) |
                Q(property_offer_client__type__icontains=search_text) |
                Q(property_offer_agent__agent__first_name__icontains=search_text) |
                Q(property_offer_agent__agent__last_name__icontains=search_text) |
                Q(property_offer_agent__agent__email__icontains=search_text) |
                Q(property_offer_agent__agent__phone_number__icontains=search_text) |
                Q(property_offer_agent__representing__icontains=search_text) |
                Q(property_type__icontains=search_text) |
                Q(property_offer_additional_documents__name__icontains=search_text) |
                Q(property_offer_condition__name__icontains=search_text) |
                Q(property_offer_additional_term__name__icontains=search_text) |
                Q(property_offer_goods_included__name__icontains=search_text) |
                Q(property_offer_notes__note__icontains=search_text),
                **offer_payload
            )

        return offers.order_by('-id').distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        user = self.request.user

        if user.is_user_manager or user.is_superuser:
            queryset = queryset
        elif user.is_agent:
            queryset = queryset.filter(property_offer_agent__agent__user__id=user.id)
        else:
            queryset = queryset.filter(property_offer_client__client__id=user.id)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Offer.objects.all().order_by('id')
        offer = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(offer)
        response = Response(serializer.data)

        return response

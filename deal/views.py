import json
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import action
from rest_framework import status, filters, viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.pagination import LargeResultsSetPagination
from core.mixins import HomeswiprCreateModelMixin, DestroyArchiveModelMixin

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
    LawFirm as DealLawFirm,
    Realtor as DealRealtor,
    DealAdditionalDocument,
    DealNote
)

from deal.serializers import (
    AdditionalTermSerializer as DealAdditionalTermSerializer,
    DealBrokerageSerializer,
    DealClientSerializer,
    CommissionSerializer,
    ConditionSerializer as DealConditionSerializer,
    DealSerializer,
    DealStatusSerializer,
    DepositSerializer as DealDepositSerializer,
    GoodsIncludedSerializer as DealGoodsIncludedSerializer,
    DealLawFirmSerializer,
    RealtorSerializer as DealRealtorSerializer,
    DealAdditionalDocumentSerializer,
    DealNoteSerializer
)


class DealAdditionalTermViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealAdditionalTermSerializer

    def get_queryset(self, *args, **kwargs):
        additional_terms = DealAdditionalTerm.active_objects.all()
        return additional_terms

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        additional_terms = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(additional_terms)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_additional_term_deal_connection(self, *args, **kwargs):
        additional_term_id = self.request.query_params.get('additional_term_id')

        if additional_term_id:
            try:
                additional_term = DealAdditionalTerm.objects.get(id=int(additional_term_id))
                additional_term.delete()
            except DealAdditionalTerm.DoesNotExist:
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


class DealBrokerageViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealBrokerageSerializer

    def get_queryset(self, *args, **kwargs):
        brokerages = DealBrokerage.active_objects.all()
        return brokerages

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        brokerages = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(brokerages)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_brokerage_deal_connection(self, *args, **kwargs):
        deal_id = self.request.query_params.get('deal_id')
        brokerage_id = self.request.query_params.get('brokerage_id')

        if deal_id and brokerage_id:
            try:
                deal_brokerage = DealBrokerage.objects.get(deal__id=int(deal_id), brokerage__id=int(brokerage_id))
                deal_brokerage.delete()
            except DealBrokerage.DoesNotExist:
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


class DealClientViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealClientSerializer

    def get_queryset(self, *args, **kwargs):
        clients = DealClient.active_objects.all()
        return clients

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        clients = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(clients)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_client_deal_connection(self, *args, **kwargs):
        deal_id = self.request.query_params.get('deal_id')
        client_id = self.request.query_params.get('client_id')

        if deal_id and client_id:
            try:
                deal_client = DealClient.objects.get(deal__id=int(deal_id), client__id=int(client_id))
                deal_client.delete()
            except DealClient.DoesNotExist:
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


class DealCommissionViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommissionSerializer

    def get_queryset(self, *args, **kwargs):
        commissions = Commission.active_objects.all()
        return commissions

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        commissions = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(commissions)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_commission_deal_connection(self, *args, **kwargs):
        commission_id = self.request.query_params.get('commission_id')

        if commission_id:
            try:
                commission = Commission.objects.get(id=int(commission_id))
                commission.delete()
            except Commission.DoesNotExist:
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


class DealConditionViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealConditionSerializer

    def get_queryset(self, *args, **kwargs):
        conditions = DealCondition.active_objects.all()
        return conditions

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        conditions = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(conditions)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_condition_deal_connection(self, *args, **kwargs):
        condition_id = self.request.query_params.get('condition_id')

        if condition_id:
            try:
                condition = DealCondition.objects.get(id=int(condition_id))
                condition.delete()
            except DealCondition.DoesNotExist:
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


class DealViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self, *args, **kwargs):
        deal_payload = {'is_active': True}
        is_archived = self.request.query_params.get('is_archived', "")
        agents = self.request.query_params.get("agents", "")
        deal_status = self.request.query_params.get("statuses", "")
        search_text = self.request.query_params.get("search_text", "")

        if is_archived and is_archived == 'True':
            deal_payload.update({'is_active': False})
        if agents:
            deal_payload.update({'realtor__agent__id__in': json.loads(agents)})
        if deal_status:
            deal_payload.update({'status__name__in': json.loads(deal_status)})

        deals = Deal.objects.filter(**deal_payload)

        if search_text:
            deals = Deal.objects.filter(
                Q(possession_date__icontains=search_text) |
                Q(representing__icontains=search_text) |
                Q(sale_price__icontains=search_text) |
                Q(sale_date__icontains=search_text) |
                Q(address__icontains=search_text) |
                Q(realtor__agent__first_name__icontains=search_text) |
                Q(realtor__agent__last_name__icontains=search_text) |
                Q(realtor__agent__full_name__icontains=search_text) |
                Q(client__client__first_name__icontains=search_text) |
                Q(client__client__last_name__icontains=search_text) |
                Q(goodsincluded__name__icontains=search_text) |
                Q(deal_deposit__amount__icontains=search_text) |
                Q(deal_deposit__payment_method__icontains=search_text),
                **deal_payload
            )

        return deals.order_by('-id').distinct()

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        user = self.request.user

        if user.is_user_manager or user.is_superuser:
            queryset = queryset
        elif user.is_agent:
            queryset = queryset.filter(realtor__agent__id=user.id)
        else:
            queryset = queryset.filter(client__client__id=user.id)

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = Deal.objects.all().order_by('id')
        conditions = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(conditions)
        response = Response(serializer.data)

        return response


class DealStatusViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealStatusSerializer

    def get_queryset(self, *args, **kwargs):
        status = DealStatus.active_objects.all()
        return status

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        status = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(status)
        response = Response(serializer.data)
        return response


class DealDepositViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealDepositSerializer

    def get_queryset(self, *args, **kwargs):
        deposits = DealDeposit.active_objects.all()
        return deposits

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        deposits = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(deposits)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_deposit_deal_connection(self, *args, **kwargs):
        deposit_id = self.request.query_params.get('deposit_id')

        if deposit_id:
            try:
                deposit = DealDeposit.objects.get(id=int(deposit_id))
                deposit.delete()
            except DealDeposit.DoesNotExist:
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


class DealGoodsIncludedViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealGoodsIncludedSerializer

    def get_queryset(self, *args, **kwargs):
        goods_included = DealGoodsIncluded.active_objects.all()
        return goods_included

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        goods_included = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(goods_included)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_goods_included_deal_connection(self, *args, **kwargs):
        goods_included_id = self.request.query_params.get('goods_included_id')

        if goods_included_id:
            try:
                deposit = DealGoodsIncluded.objects.get(id=int(goods_included_id))
                deposit.delete()
            except DealGoodsIncluded.DoesNotExist:
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


class DealLawFirmViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealLawFirmSerializer

    def get_queryset(self, *args, **kwargs):
        law_firms = DealLawFirm.active_objects.all()
        return law_firms

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        law_firms = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(law_firms)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_law_firm_deal_connection(self, *args, **kwargs):
        deal_id = self.request.query_params.get('deal_id')
        law_firm_id = self.request.query_params.get('law_firm_id')

        if deal_id and law_firm_id:
            try:
                deal_client = DealLawFirm.objects.get(deal__id=int(deal_id), lawfirm__id=int(law_firm_id))
                deal_client.delete()
            except DealLawFirm.DoesNotExist:
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


class DealRealtorViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealRealtorSerializer

    def get_queryset(self, *args, **kwargs):
        realtors = DealRealtor.active_objects.all()
        return realtors

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        realtors = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(realtors)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_realtor_deal_connection(self, *args, **kwargs):
        deal_id = self.request.query_params.get('deal_id')
        realtor_id = self.request.query_params.get('realtor_id')

        if deal_id and realtor_id:
            try:
                deal_client = DealRealtor.objects.get(deal__id=int(deal_id), agent__id=int(realtor_id))
                deal_client.delete()
            except DealRealtor.DoesNotExist:
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


class DealNoteViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealNoteSerializer

    def get_queryset(self, *args, **kwargs):
        deal_id = self.request.query_params.get('deal', None)
        deal_note = DealNote.active_objects.all()

        if deal_id:
            deal_note = deal_note.filter(deal__id=int(deal_id))

        return deal_note

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        deal_note = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(deal_note)
        response = Response(serializer.data)
        return response

    @action(detail=False, methods=["delete"])
    def delete_note_deal_connection(self, *args, **kwargs):
        deal_note_id = self.request.query_params.get('deal_note_id')

        if deal_note_id:
            try:
                deposit = DealNote.objects.get(id=int(deal_note_id))
                deposit.delete()
            except DealNote.DoesNotExist:
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


class DealAdditionalDocumentViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    UpdateModelMixin,
    DestroyArchiveModelMixin
):
    permission_classes = (IsAuthenticated,)
    serializer_class = DealAdditionalDocumentSerializer

    def get_queryset(self, *args, **kwargs):
        deal_id = self.request.query_params.get('deal', None)
        deal_attachment_document = DealAdditionalDocument.active_objects.all()

        if deal_id:
            deal_attachment_document = deal_attachment_document.filter(deal__id=int(deal_id))

        return deal_attachment_document

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        deal_attachment_document = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(deal_attachment_document)
        response = Response(serializer.data)

        return response

    @action(detail=False, methods=["delete"])
    def delete_additional_document_deal_connection(self, *args, **kwargs):
        additional_document_id = self.request.query_params.get('additional_document_id')

        if additional_document_id:
            try:
                additional_document = DealAdditionalDocument.objects.get(id=int(additional_document_id))
                additional_document.delete()
            except DealAdditionalDocument.DoesNotExist:
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
from rest_framework import routers

from deal.views import (
    DealAdditionalTermViewSet,
    DealBrokerageViewSet,
    DealClientViewSet,
    DealCommissionViewSet,
    DealConditionViewSet,
    DealViewSet,
    DealStatusViewSet,
    DealDepositViewSet,
    DealGoodsIncludedViewSet,
    DealLawFirmViewSet,
    DealRealtorViewSet,
    DealAdditionalDocumentViewSet,
    DealNoteViewSet
)

router = routers.SimpleRouter()

app_name = "deal"

router.register("note", DealNoteViewSet, basename='DealNote')
router.register("additional_document", DealAdditionalDocumentViewSet, basename='DealAdditionalDocument')
router.register("additional_term", DealAdditionalTermViewSet, basename='DealAdditionalTerm')
router.register("brokerage", DealBrokerageViewSet, basename='DealBrokerage')
router.register("client", DealClientViewSet, basename='DealClient')
router.register("commission", DealCommissionViewSet, basename='DealCommission')
router.register("condition", DealConditionViewSet, basename='DealCondition')
router.register("status", DealStatusViewSet, basename='DealStatus')
router.register("deposit", DealDepositViewSet, basename='DealDeposit')
router.register("goods_included", DealGoodsIncludedViewSet, basename='DealGoodsIncluded')
router.register("law_firm", DealLawFirmViewSet, basename='DealLawFirm')
router.register("realtor", DealRealtorViewSet, basename='DealRealtor')
router.register("", DealViewSet, basename='Deal')

urlpatterns = []
urlpatterns += router.urls

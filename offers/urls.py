from rest_framework import routers
from offers.views import (
    OfferViewSet,
    OfferStatusViewSet,
    OfferClientViewSet,
    OfferAgentViewSet,
    OfferNoteViewSet,
    RequirementViewSet,
    ConditionViewSet,
    AdditionalTermViewSet,
    DepositViewSet,
    GoodsIncludedViewSet,
    OfferOfferAdditionalDocumentsViewSet
)


router = routers.SimpleRouter()

app_name = "offer"

router.register(r"offer_status", OfferStatusViewSet, basename="OfferStatus")
router.register(r"client", OfferClientViewSet, basename="OfferClient")
router.register(r"note", OfferNoteViewSet, basename="OfferNote")
router.register(r"additional_documents", OfferOfferAdditionalDocumentsViewSet, basename="OfferAdditionalDocuments")
router.register(r"agent", OfferAgentViewSet, basename="OfferAgent")
router.register(r"requirement", RequirementViewSet, basename="OfferRequirement")
router.register(r"condition", ConditionViewSet, basename="OfferCondition")
router.register(r"additional_term", AdditionalTermViewSet, basename="OfferAdditionalTerm")
router.register(r"deposit", DepositViewSet, basename="OfferDeposit")
router.register(r"goods_included", GoodsIncludedViewSet, basename="OfferGoodsIncluded")
router.register(r"", OfferViewSet, basename="Offer")

urlpatterns = []

urlpatterns += router.urls

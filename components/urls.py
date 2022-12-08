from rest_framework import routers
from components.views import (
    BrokerageViewSet,
    AgentViewSet,
    LawFirmViewSet,
    GoodsIncludedViewSet,
    ConditionViewSet,
    ConditionStatusViewSet,
    AdditionalTermsViewSet,
    PaymentMethodViewSet,
    PropertyTypeViewSet,
    AttachmentsViewSet,
    UnreadNoteViewSet
)


router = routers.SimpleRouter()

app_name = "component"

router.register(r"brokerage", BrokerageViewSet, basename="Brokerage")
router.register(r"agent", AgentViewSet, basename="Agent")
router.register(r"law_firm", LawFirmViewSet, basename="LawFirm")
router.register(r"goods_inlcuded", GoodsIncludedViewSet, basename="GoodsIncluded")
router.register(r"condition", ConditionViewSet, basename="Condition")
router.register(r"condition_status", ConditionStatusViewSet, basename="ConditionStatus")
router.register(r"additional_terms", AdditionalTermsViewSet, basename="AdditionalTerms")
router.register(r"payment_method", PaymentMethodViewSet, basename="PaymentMethod")
router.register(r"property_type", PropertyTypeViewSet, basename="PropertyType")
router.register(r"attachments", AttachmentsViewSet, basename="Attachments")
router.register(r"unread_note", UnreadNoteViewSet, basename="UnreadNote")

urlpatterns = []

urlpatterns += router.urls

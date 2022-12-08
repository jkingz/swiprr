from rest_framework import routers

from leads.views import (
    LeadViewSet,
    LeadStatusViewSet,
    LeadAgentsViewSet,
    LeadContactViewSet,
    NoteViewSet,
    FinancialStatusViewSet,
    ContactTypeViewSet,
    LeadWarmthViewSet,
    TimeFrameViewSet,
    LeadMortgageBrokerViewSet,
    LeadSalesAgentViewSet
)

router = routers.SimpleRouter()

app_name = "leads"

router.register("time_frame", TimeFrameViewSet, basename='TimeFrame')
router.register("lead_warmth", LeadWarmthViewSet, basename='LeadWarmth')
router.register("contact_type", ContactTypeViewSet, basename='ContactType')
router.register("financial_status", FinancialStatusViewSet, basename='FinancialStatus')
router.register("notes", NoteViewSet, basename='Notes')
router.register("lead_contacts", LeadContactViewSet, basename='LeadContacts')
router.register("lead_agents", LeadAgentsViewSet, basename='LeadAgents')
router.register("lead_status", LeadStatusViewSet, basename='LeadStatus')
router.register("mortgage_broker", LeadMortgageBrokerViewSet, basename="MortgageBroker")
router.register("sales_agent", LeadSalesAgentViewSet, basename="LeadSalesAgent")
router.register("", LeadViewSet, basename='Lead')

urlpatterns = []
urlpatterns += router.urls

from rest_framework import routers

from contacts.views import (
    ContactViewSet,
    ContactAgentViewSet,
    ContactNoteViewSet,
    ContactMortgageBrokerViewSet,
    ContactSalesAgentViewSet
)

router = routers.SimpleRouter()

app_name = "contacts"


router.register("agent", ContactAgentViewSet, basename='ContactAgent')
router.register("note", ContactNoteViewSet, basename='ContactNote')
router.register("mortgage_broker", ContactMortgageBrokerViewSet, basename="ContactMortgageBroker")
router.register("sales_agent", ContactSalesAgentViewSet, basename="ContactSalesAgent")
router.register("", ContactViewSet, basename='Contact')

urlpatterns = []
urlpatterns += router.urls

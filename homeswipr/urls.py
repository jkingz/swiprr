from rest_framework import routers

from .views import (
    FrequentlyAskedQuestionViewSet,
    GeneralPropertyViewSet,
    MyFavoriteAgentViewSet,
    MyFavoritePropertyViewSet,
    PropertyInquiryViewSet,
    PropertyManagementView,
    UserSavedSearchViewSet,
    AddressViewSet
)

router = routers.SimpleRouter()

app_name = "homeswiper"

router.register(r"property", GeneralPropertyViewSet, basename="property")
# TODO: Change the url into /my_favorites/property
router.register(
    r"favorited/property", MyFavoritePropertyViewSet, basename="favorited-properties"
)
router.register(r"favorited/agent", MyFavoriteAgentViewSet, basename="favorited-agents")
router.register(r"saved_search", UserSavedSearchViewSet, basename="saved-search")
router.register(
    r"frequently_asked", FrequentlyAskedQuestionViewSet, basename="frequently-asked"
)
router.register(
    r"property_inquiry", PropertyInquiryViewSet, basename="property-inquiry"
)

router.register(r"property_management", PropertyManagementView, basename="property-management")

router.register(
    r"address", AddressViewSet, basename="address"
)


urlpatterns = []

urlpatterns += router.urls

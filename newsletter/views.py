from core.mixins import HomeswiprCreateModelMixin
from core.pagination import StandardResultsSetPagination
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from .models import NewsLetter
from .serializers import NewsLetterSerializer


class NewsLetterViewSet(
    viewsets.ViewSet,
    GenericAPIView,
    ListModelMixin,
    RetrieveModelMixin,
    HomeswiprCreateModelMixin,
):
    """
    Gets all the property follow view set

    # ListModelMixin -> Used for listing newsletter
    # RetrieveModelMixin -> Used for retrieving data on a single newsletter
    # HomeswiprCreateModelMixin -> Used for the post method create a newsletter
    """

    serializer_class = NewsLetterSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = []
        if self.action == "create":
            # TODO: Extend the user model from django and add another attribute?
            # or maybe use is_staff or is_admin.
            permission_classes += []
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        search_text = self.request.data.get("search_text", "")

        # NOTE: Don't use select or prefetch related here.
        # Prefetch and select uses 'inner join' and 'IN' on the database;
        # Which means if a newsletter with no tags is found, our database
        # won't fetch it.

        # Sample usecase situation: If for some reason, the staff didn't add a tag
        # on initial save and want to update it.
        return (
            NewsLetter.objects.filter(
                title__icontains=search_text,
                body__icontains=search_text,
                tags__name__icontains=search_text,
            )
            .order_by("-date_created")
            .distinct()
        )

    def create(self, *args, **kwargs):
        return self.create_with_passed_requests_on_serializer(*args, **kwargs)

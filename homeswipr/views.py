import math
from datetime import timedelta

import requests

from decouple import config
from core.mixins import DestroyArchiveModelMixin, HomeswiprCreateModelMixin
from core.pagination import (
    AutoCompleteSetPagination,
    FavoritesSetPagination,
    NearbyListingsSetPagination,
    StandardResultsSetPagination,
)
from core.permissions import ObjectOwnerPermission, ObjectOwnerPermissionOrUserManager
from core.shortcuts import convert_query_params_to_boolean
from core.utils import HomeswiprMailer, PropertyUploadManager, PropertyGeolocationManager
from crea_parser.models import Property, PropertyInfo, Address, PropertyPhoto, Building, AgentDetails, Geolocation, Land, Phone, Room
from crea_parser.submodels.metadata import PropertyPropertyType, PropertyTransactionType, PropertyArchitecturalStyle, PropertyMeasureUnit, PropertyRoomType, PropertyRoomLevel
from django.contrib.auth import get_user, get_user_model
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.cache import cache
from django.db.models import Max, Q, Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.formats import number_format
from homeswipr.serializers import (
    AddressAutoCompleteSerializer,
    AgentFavoriteSerializer,
    CreatePropertyFavoriteSerializer,
    FrequentlyAskedQuestionSerializer,
    ListUserSavedSearchWitahAdminSerializer,
    PropertyFavoriteSerializer,
    PropertyInquirySerializer,
    PropertyExpandedSerializer,
    PropertySerializer,
    UserSavedSearchSerializer,
    AddressCommunityCitySerializer,
    PropertyPhotoSerializer,
    PropertyOnlySerializer,
    FeedBackSerializer
)
from rest_framework import filters, status, viewsets, views
from rest_framework.decorators import action, permission_classes
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import UserHistory
from users.permissions import IsUserManager, IsAgent

from .exceptions import LngAndLatIsNotPassed
from .mixins import FavoriteHelperMixin, NullsLastOrderFilterMixin, PropertyHelperMixin
from .models import (
    AgentFavorite,
    FrequentlyAskedQuestion,
    PropertyFavorite,
    PropertyInquiry,
    UserSavedSearch,
)
from .tasks import cache_listing_counts
from .permissions import SavedSearchOwnerPermission

from .utils import (
    _send_client_notification,
    _send_agent_notification,
    _send_admin_notification,
)

from .constants import (
    EmailType,
    ClientMessages,
    AgentMessages,
    AdminMessages
)


class GeneralPropertyViewSet(
    NullsLastOrderFilterMixin,
    viewsets.GenericViewSet,
    PropertyHelperMixin,
    ListModelMixin,
    RetrieveModelMixin,
    HomeswiprCreateModelMixin,
):
    """
    Property viewsets that concerns itself on the normal user (not admin stuff)
    If you're looking for user manager viewset, property, That should be located on
    users/views

    NOTE: Change the http restrictions into a permission type
    to make the team's http restriction uniform, and combine multiple
    related views into a single model viewset in the future if we
    have time
    """

    pagination_class = StandardResultsSetPagination

    # A listing id is equal with the search text
    mls_matched = False

    filter_backends = [filters.OrderingFilter]
    ordering = "-pk"
    ordering_fields = [
        "listing_id",
        "Address__street_address",
        "Address__city",
        "Info__transaction_type__short_value",
        "Info__price",
        "Building__size_interior_display",
        "Info__date_created",
        "Info__listing_contract_date",
        "Building__bathroom_total",
        "Building__bedrooms_total",
        "general_price",
    ]

    def get_permissions(self, *args, **kwargs):
        # NOTE: Maybe we should put this on a single permission class?

        if self.action == "retrieve":
            # Remove every permission on property detail,
            # this allows this page to be shared to anyone
            permission_classes = []
        elif self.action == "recently_viewed":
            permission_classes = [IsAuthenticated, SavedSearchOwnerPermission]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsAgent]
        else:
            permission_classes = [SavedSearchOwnerPermission]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.filter_valid_property(self.get_base_property())

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "create":
            return PropertyExpandedSerializer
        return PropertySerializer

    def list(self, *args, **kwargs):
        """
        The endpoint of the advance search. This passes multiple parameters to
        filter the property of the user.

        Optional Params:
            search_text - Hits most of the address and mls number match
            lower_boundary_price_range - Greater than or equal this price
            upper_boundary_price_range - Less than or equal this price
            least_amount_of_bedroom - Least amount of the bedroom
            least_amount_of_bathroom - Least amount of bathroom
            transaction_type_id - The transaction type id to filter (Only pass a single one)
            ownership_type_ids - The ownership type ids (plural) to filter
            community_list_search_text - Hits the community fields (Like Subdivision and Stuff)
            has_video - Has video or noy
            from_creation_date - Greater than or equal this creation date
            until_creation_date - Less than or equal this creation date
            from_listing_contract_date - Greater than or equal this listing contract date
            until_listing_contract_date - Less than or equal this listing creation date
            saved_search_pk - If this sent, use the fields defined on the saved search instead of the
                              params above
            show_only_new_ones - Get properties later than the last checked date

        # NOTE: If saved search pk is passed, Disregard most of the parameters
        # to use the fields on the saved search
        # NOTE: Search text can match with mls number. If it matches, this return
        # a queryset with single instance regardless of the parameters defined.
        """

        # Rewrite the saved search date, so the emailer will try to get the future
        # date from "now".
        # Advance Search
        saved_search_pk = self.request.query_params.get("saved_search_pk", None)

        saved_search_last_check_date = None

        if saved_search_pk:
            user_saved_search = UserSavedSearch.active_objects.get(pk=saved_search_pk)
            # This checks to only get the new ones from saved search
            show_only_new_ones = convert_query_params_to_boolean(
                self.request.query_params.get("show_only_new_ones", False)
            )
            if show_only_new_ones:
                saved_search_last_check_date = user_saved_search.last_checked_date
            user_saved_search.last_checked_date = timezone.now()
            user_saved_search.save()

        final_params = self.construct_advance_search_parameters(saved_search_pk)

        # Get the parameters from query_params instead of data
        # since we are using a get method
        search_text = final_params.get("search_text", "")
        # Queryset are not run until evaluated
        queryset = self.get_queryset()

        # Advance Search
        queryset = self.filter_property_by_keyword(queryset, search_text)
        queryset = self.advance_search(queryset, final_params)

        if saved_search_last_check_date:
            queryset = queryset.filter(
                creation_date__gt=saved_search_last_check_date
            )

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["mls_matched"] = self.mls_matched
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        response.data["mls_matched"] = self.mls_matched
        return response

    def retrieve(self, *args, **kwargs):
        # Override here just to save the user history
        if self.request.user.is_authenticated:
            view_history = UserHistory(
                content_object=self.get_object(),
                user=self.request.user,
                history_type=UserHistory.VIEWED,
            )

            view_history.save()

        return super().retrieve(*args, **kwargs)

    @action(detail=False, methods=["get"])
    def recently_added(self, *args, **kwargs):
        cache_key = "luxurious_houses"

        cached_value = cache.get(cache_key)
        data = None

        lng = self.request.query_params.get("lng", None)
        lat = self.request.query_params.get("lat", None)

        if cached_value is not None and lat is not None and lng is not None:
            data = cached_value
            if data.get("count") != 0:
                return Response(data)

        queryset = self.get_queryset()

        queryset = self.load_other_section_page_filters(
            queryset, self.request.query_params
        ).distinct()

        property_age_subtractor = 0

        recently_added_has_more_than_fifteen_count = False

        # Check a result that has a proper result count
        while not recently_added_has_more_than_fifteen_count:

            property_age_subtractor += 14
            limited_queryset = None

            limited_queryset = queryset.filter(
                Info__listing_contract_date__gte=timezone.now()
                - timedelta(days=property_age_subtractor)
            )

            # Increase count until we can return a proper count
            # Only add until up to 6 months (180 days), if we can't
            # found a proper result, resort to no limit on how many
            # listing age date (This is to avoid an inifite loop!)
            if limited_queryset.count() > 15:
                queryset = limited_queryset
                recently_added_has_more_than_fifteen_count = True
            elif property_age_subtractor > 181:
                recently_added_has_more_than_fifteen_count = True

        if not self.request.query_params.get("ordering"):
            self.ordering = "-Info__listing_contract_date"

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        cache.set(cache_key, serializer.data, 2 * 60 * 60)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recently_viewed(self, *args, **kwargs):
        # Annotate should pull the date created and put the max (latest)
        # to our property table
        queryset = (
            self.get_queryset()
            .filter(
                user_history__user=self.request.user,
                user_history__history_type=UserHistory.VIEWED,
            )
            .annotate(created=Max("user_history__date_created"))
            .distinct()
        )

        include_geo_location = False

        queryset = self.load_other_section_page_filters(
            queryset, self.request.query_params, include_geo_location
        )

        if not self.request.query_params.get("ordering"):
            self.ordering = "-created"

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def luxurious_houses(self, *args, **kwargs):

        cache_key = "luxurious_houses"

        cached_value = cache.get(cache_key)
        data = None

        lng = self.request.query_params.get("lng", None)
        lat = self.request.query_params.get("lat", None)

        if cached_value is not None and lat is not None and lng is not None:
            data = cached_value
            if data.get("count") != 0:
                return Response(data)

        queryset = self.get_queryset()

        queryset = self.load_other_section_page_filters(
            queryset, self.request.query_params
        )

        # Order by the creation date
        queryset = queryset.exclude(Info__price=None)
        queryset = queryset.filter(
            Info__property_type__metadata_entry_id=PropertyPropertyType.SINGLE_FAMILY_METADATA_ENTRY_ID,
            Info__price__gte=1000000,
        )
        queryset = queryset.distinct()


        if not self.request.query_params.get("ordering"):
            self.ordering = "-Info__price"

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        cache.set(cache_key, serializer.data, 2 * 60 * 60)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def count_results(self, *args, **kwargs):
        # TODO: Change the implementation of this
        # now that permissions are removed

        search_texts = self.request.query_params.getlist("search_texts[]", [])

        cache_key = "count_results"

        cache_value = cache.get(cache_key)

        data = None

        if cache_value is not None:
            data = cache_value
        else:
            queryset = self.get_queryset().order_by("-last_updated")
            data = {"search_counts": {}}
            for search_text in search_texts:
                # Yup, this loops queries but this should only get the count
                # and it's also better than the other options which is to preload
                # and count
                data["search_counts"][search_text] = (
                    queryset.filter(Q(Address__city__icontains=search_text))
                    .distinct()
                    .count()
                )

            # Make the cache expire on 24 hours
            cache.set(cache_key, data, 24 * 60 * 60)
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def all_property_count(self, *args, **kwargs):
        data = None

        cache_key = "all_property_count"
        cache_value = cache.get(cache_key)

        if cache_value is not None:
            data = cache_value
        else:
            cache_listing_counts.delay(cache_key)
            data = "100,000"

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], pagination_class=AutoCompleteSetPagination)
    def address_auto_complete(self, *args, **kwargs):
        search_text = self.request.query_params.get("search_text", "")

        queryset = self.get_queryset()

        queryset = (
            queryset.filter(
                Q(Address__street_address__startswith=search_text)
                | Q(Address__address_line1__startswith=search_text)
            )
            .select_related("Address")
            .order_by("-last_updated")
            .distinct()
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = AddressAutoCompleteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AddressAutoCompleteSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], pagination_class=AutoCompleteSetPagination)
    def community_auto_complete(self, *args, **kwargs):
        community_search = self.request.query_params.get("community_search", "")

        queryset = self.get_queryset()

        queryset = (
            queryset.filter(
                Address__community_name__startswith=community_search
            )
            .select_related("Address")
            .order_by("-last_updated")
            .distinct()
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = AddressAutoCompleteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AddressAutoCompleteSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], pagination_class=NearbyListingsSetPagination)
    def nearby_homes(self, *args, **kwargs):

        # Get the parameters from query_params instead of data
        # since we are using a get method
        search_text = self.request.query_params.get("search_text", "")
        lng = self.request.query_params.get("lng", None)
        lat = self.request.query_params.get("lat", None)

        if lng is None or lat is None:
            raise LngAndLatIsNotPassed

        user_coordinates = Point(float(lng), float(lat))
        queryset = (
            self.get_queryset()
            .filter(
                Geo__coordinates__dwithin=(user_coordinates, 0.08),
                Geo__coordinates__distance_lte=(user_coordinates, D(km=8)),
            )
            .annotate(distance=Distance("Geo__coordinates", user_coordinates))
            .order_by("distance")
            .distinct()
        )

        queryset = self.filter_property_by_keyword(queryset, search_text)

        if not self.request.query_params.get("ordering"):
            self.ordering = "distance"

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def propz_houses(self, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = self.load_other_section_page_filters(
            queryset, self.request.query_params
        )

        queryset = queryset.filter(
            listing_type=2,
        )

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def upload_house_images(self, *args, **kwargs):
        assigned_property = get_object_or_404(Property, id=kwargs["pk"])
        images = self.request.data.getlist('image')
        property_uploader = PropertyUploadManager(images)
        count = 1
        photo_list = []
        for image in images:
            upload, key = property_uploader.upload_image(image, count, assigned_property.id)
            if upload:
                photo = PropertyPhoto(
                    sequence_id=count,
                    connected_property=assigned_property,
                    large_photo_url=key,
                    photo_url=key,
                    thumbnail_url=key
                )
                photo.save()
                photo_list.append(photo)
            count = count + 1
        serializer = PropertyPhotoSerializer(photo_list, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def delete_property(self, *args, **kwargs):
        property_to_hide = get_object_or_404(
            Property, id=kwargs["pk"],
            listing_type=2,
            is_active=True
        )
        property_to_hide.is_active = False
        property_to_hide.save()

        serializer = PropertyOnlySerializer(property_to_hide)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def update_property(self, *args, **kwargs):
        # import pdb;pdb.set_trace()
        property_to_update = get_object_or_404(
            Property, id=kwargs.get("pk"),
            listing_type=2,
            is_active=True
        )

        # Address
        address = get_object_or_404(
            Address,
            connected_property=property_to_update
        )
        address.street_address = self.request.data.get("Address")["street_address"]
        address.address_line1 = self.request.data.get("Address")["address_line1"]
        address.address_line2 = self.request.data.get("Address")["address_line2"]
        address.city = self.request.data.get("Address")["city"]
        address.province = self.request.data.get("Address")["province"]
        address.postal_code = self.request.data.get("Address")["postal_code"]
        address.community_name = self.request.data.get("Address")["community_name"]
        address.neighbourhood = self.request.data.get("Address")["neighbourhood"]
        address.save()

        # PropertyInfo
        info = get_object_or_404(
            PropertyInfo,
            listing_type=2,
            connected_property=property_to_update
        )

        get_property_type = get_object_or_404(
            PropertyPropertyType,
            pk=self.request.data.get("Info")["property_type"]
        )
        get_transaction_type = get_object_or_404(
            PropertyTransactionType,
            pk=self.request.data.get("Info")["transaction_type"]
        )

        info.property_type = get_property_type
        info.price = self.request.data.get("Info")["price"]
        info.transaction_type = get_transaction_type
        info.public_remarks = self.request.data.get("Info")["public_remarks"]
        info.save()

        try:
            if self.request.data.get("Info", None)["features"]:
                features = self.request.data.get("Info", None)["features"]
                info.features.set(features)
        except Exception as e:
            print(e)
        try:
            if self.request.data.get("Info", None)["storage_type"]:
                storage_types = self.request.data.get("Info", None)["storage_type"]
                info.storage_type.set(storage_types)
        except Exception as e:
            print(e)
        try:
            if self.request.data.get("Info", None)["structure"]:
                structures = self.request.data.get("Info", None)["structure"]
                info.structure.set(structures)
        except Exception as e:
            print(e)
        info.save()

        # Building
        try:
            building = get_object_or_404(
                Building,
                connected_property=property_to_update
            )
            building.bathroom_total = self.request.data.get('bathroom_total')
            building.bedrooms_total = self.request.data.get('bedrooms_total')
            building.bedrooms_above_ground = self.request.data.get('bedrooms_above_ground')
            building.bedrooms_below_ground = self.request.data.get('bedrooms_below_ground')
            building.constructed_date = self.request.data.get("Building")["constructed_date"]
            building.architectural_style.set(self.request.data.get("Building")["architectural_style"])
            building.size_interior = self.request.data.get("Building")["size_interior"]

            size_interior_unit_choice = get_object_or_404(PropertyMeasureUnit, pk=self.request.data.get("Building")["size_interior_unit"])
            if size_interior_unit_choice:
                building.size_interior_unit = size_interior_unit_choice
            if self.request.data.get("Building", None)["foundation_type"]:
                foundation_types = self.request.data.get("Building", None)["foundation_type"]
                building.foundation_type.set(foundation_types)
            building.save()
        except Exception as e:
            print(e)

        # Land
        try:
            land = get_object_or_404(
                Land,
                connected_property=property_to_update,
            )
            land.size_total = self.request.data.get("land")["size_total"]
            size_total_unit_choice = get_object_or_404(PropertyMeasureUnit, pk=self.request.data.get("land")["size_total_unit"])
            if size_total_unit_choice:
                land.size_total_unit = size_total_unit_choice
            land.save()
        except Exception as e:
            print(e)

        # Geolocation
        try:
            if self.request.data.get("Geolocation", None)["longitude"] and self.request.data.get("Geolocation", None)["latitude"]:
                geolocation = get_object_or_404(
                    Geolocation,
                    connected_property=property_to_update
                )
                geolocation.coordinates = Point(
                    float(self.request.data.get("Geolocation")["longitude"]),
                    float(self.request.data.get("Geolocation")["latitude"])
                )
                geolocation.save()
        except Exception as e:
            print(e)

        serializer = PropertyOnlySerializer(property_to_update)

        # get geolocation if available
        request_result, request_made = PropertyGeolocationManager.add_geolocation(property_to_update, address)

        # Rooms
        if self.request.data.get("Room", None)["model_type"] and self.request.data.get("Room", None)["level"] and self.request.data.get("Room", None)["dimension"]:
            # Delete existing dimensions
            Room.objects.filter(
                connected_property=property_to_update
            ).delete()
            #add new updated dimensions
            count = 0
            for index in self.request.data.get("Room", None)["model_type"]:
                model_type = get_object_or_404(PropertyRoomType, pk=self.request.data.get("Room", None)["model_type"][count])
                level = get_object_or_404(PropertyRoomLevel, pk=self.request.data.get("Room", None)["level"][count])
                if model_type and level:
                    room = Room(
                        connected_property=property_to_update,
                        model_type=model_type,
                        level=level,
                        dimension=self.request.data.get("Room", None)["dimension"][count]
                    )
                    room.save()
                count = count + 1


        #update agent if agent is updated and user updating is admin
        if self.request.user.is_superuser or self.request.user.is_user_manager and self.request.data.get("Agent", None) != None:
            if self.request.data.get("Agent", None):
                # delete agents related to property
                AgentDetails.objects.filter(
                    connected_property=property_to_update
                ).delete()
                # add new agent for property
                new_agents = self.request.data.get("Agent")
                for new_agent in new_agents:
                    agent = AgentDetails.objects.create(
                        name=new_agent["name"],
                        connected_property=property_to_update
                    )
                    if new_agent["phone_number"]:
                        phone = Phone.objects.create(
                            text=new_agent["phone_number"],
                            agent=agent
                        )

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def delete_images_on_property(self, *args, **kwargs):
        property_to_update = get_object_or_404(
            Property,
            id=kwargs.get("pk"),
            listing_type=2,
            is_active=True
        )
        # delete existing property photos
        PropertyPhoto.objects.filter(
            connected_property=property_to_update
        ).delete()
        serializer = PropertyOnlySerializer(property_to_update)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def archived_propz_houses(self, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = Property.objects.filter(
            listing_type=2,
            is_active=False
        )

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def unarchive_property(self, *args, **kwargs):
        property_to_unhide = get_object_or_404(
            Property, id=kwargs["pk"],
            listing_type=2,
            is_active=False
        )
        property_to_unhide.is_active = True
        property_to_unhide.save()

        serializer = PropertyOnlySerializer(property_to_unhide)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def unassign_agents_for_property(self, *args, **kwargs):
        property_to_update = get_object_or_404(
            Property, id=kwargs["pk"],
            listing_type=2,
        )

        AgentDetails.objects.filter(
            connected_property=property_to_update
        ).delete()

        serializer = PropertyOnlySerializer(property_to_update)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def become_an_agent_property(self, *args, **kwargs):
        property_to_update = get_object_or_404(
            Property, id=kwargs["pk"],
            listing_type=2,
        )

        name = self.request.user.first_name + " " + self.request.user.last_name
        agent = AgentDetails.objects.create(
            name=name,
            connected_property=property_to_update
        )
        if self.request.user.phone_number:
            phone = Phone.objects.create(
                text=self.request.user.phone_number,
                agent=agent
            )

        serializer = PropertyOnlySerializer(property_to_update)
        return Response(serializer.data)


class MyFavoritePropertyViewSet(
    viewsets.GenericViewSet,
    FavoriteHelperMixin,
    ListModelMixin,
    DestroyArchiveModelMixin,
    HomeswiprCreateModelMixin,
):
    """
    Gets all the property favorite view set

    NOTE: Change the http restrictions into a permission type
    to make the team's http restriction uniform, and combine multiple
    related views into a single model viewset in the future if we
    have time
    """

    pagination_class = FavoritesSetPagination

    filter_backends = [filters.OrderingFilter]
    ordering = "-pk"
    ordering_fields = [
        "favorited_property__Info__date_created",
        "favorited_proeprty__Info__listing_contract_date",
        "favorited_property__Building__bathroom_total",
        "favorited_property__Building__bedrooms_total",
        "general_price",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return CreatePropertyFavoriteSerializer
        return PropertyFavoriteSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == "destroy":
            permission_classes += [ObjectOwnerPermission]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):

        search_text = self.request.query_params.get("search_text", "")

        queryset = PropertyFavorite.active_objects.select_related(
            "favorited_property",
            "favorited_property__Address",
        ).annotate(
            general_price=Coalesce(
                "favorited_property__Info__price",
                "favorited_property__Info__lease",
            )
        )

        queryset = queryset.filter(favorited_property__is_active=True)

        queryset = self.filter_favorite_by_address(queryset, search_text)

        return queryset

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = queryset.filter(user=self.request.user)

        # ordering filter
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        return response

    def create(self, *args, **kwargs):
        return self.create_with_passed_requests_on_serializer(*args, **kwargs)


class MyFavoriteAgentViewSet(
    viewsets.GenericViewSet,
    HomeswiprCreateModelMixin,
    DestroyArchiveModelMixin,
    ListModelMixin,
):
    """
    Gets all the favorite view set

    NOTE: Change the http restrictions into a permission type
    to make the team's http restriction uniform, and combine multiple
    related views into a single model viewset in the future if we
    have time
    """

    serializer_class = AgentFavoriteSerializer
    pagination_class = FavoritesSetPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [IsAuthenticated]
        if self.action == "destroy":
            permission_classes += [ObjectOwnerPermission]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        search_text = self.request.data.get("search_text", "")
        return (
            AgentFavorite.active_objects.filter(
                Q(favorited_agent__name__icontains=search_text),
                favorited_agent__is_active=True,
            )
            .select_related("favorited_agent")
            .order_by("-date_created")
        )

    def list(self, *args, **kwargs):
        queryset = self.get_queryset()

        queryset = queryset.filter(user=self.request.user)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        return response

    def create(self, *args, **kwargs):
        return self.create_with_passed_requests_on_serializer(*args, **kwargs)


class UserSavedSearchViewSet(
    viewsets.ModelViewSet, HomeswiprCreateModelMixin, DestroyArchiveModelMixin
):

    pagination_class = AutoCompleteSetPagination
    #permission_classes = (IsAuthenticated, ObjectOwnerPermissionOrUserManager)
    serializer_class = UserSavedSearchSerializer

    def get_queryset(self, *args, **kwargs):
        search_text = self.request.query_params.get("search_text", "")
        return UserSavedSearch.active_objects.filter(
                Q(title__icontains=search_text)
                | Q(search_text__icontains=search_text)
                | Q(user__first_name__icontains=search_text)
                | Q(user__last_name__icontains=search_text)
                | Q(user__email__icontains=search_text)
            ).order_by("-pk")

    def _mark_serializer(self, *args, **kwargs):
        # Marks the serializer for the update and create
        if bool(
            self.request.user.is_authenticated
            and (self.request.user.is_user_manager or self.request.user.is_superuser)
        ):
            self.serializer_class.from_admin_view = True
        else:
            self.serializer_class.from_admin_view = False

    def create(self, *args, **kwargs):
        self._mark_serializer(*args, **kwargs)
        return self.create_with_passed_requests_on_serializer(*args, **kwargs)

    def update(self, *args, **kwargs):
        # Check if the user is user manager or super user, and set
        # permission based on this
        self._mark_serializer(*args, **kwargs)
        return super().update(*args, **kwargs)

    def list(self, *args, **kwargs):
        # Get the parameters from query_params instead of data
        # since we are using a get method
        queryset = self.get_queryset()
        # For admin list
        if bool(self.request.user.is_authenticated and (self.request.user.is_user_manager or self.request.user.is_superuser)):
            self.serializer_class = ListUserSavedSearchWitahAdminSerializer
        elif bool(self.request.user.is_authenticated and self.request.user.is_agent):
            self.serializer_class = ListUserSavedSearchWitahAdminSerializer
            queryset = queryset.filter(
                user__id=self.request.user.id
            )
        else:
            # Not a user manager or a superuser.
            queryset = queryset.filter(
                user=self.request.user
            )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        return response

    @action(
        detail=False,
        methods=["post"],
        permission_classes=(
            IsAuthenticated,
            IsUserManager,
        ),
    )
    def create_saved_search_with_admin(self, *args, **kwargs):
        # TODO: Need to combine this with the normal
        # create and remove permission check on the frontend
        return self.create(*args, **kwargs)

    @action(detail=True, methods=["post"], name="Assign booking")
    def assign_agents(self, request, pk=None):
        agents = request.data.get("agents", None)
        emails = [agent.get('email') for agent in agents]
        queryset = self.get_queryset()
        try:
            saved_search = queryset.get(pk=int(pk))
            for agent in agents:
                user = get_user_model().objects.get(email=agent.get('email'))
                saved_search.agents.add(user)
            # list of agents to be removed.
            to_remove = saved_search.agents.exclude(email__in=emails)
            if to_remove:
                for agent in to_remove:
                    saved_search.agents.remove(agent)
        except UserSavedSearch.DoesNotExist:
            return Response(
                {"detail": "Assigned to value is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(saved_search).data
        _send_agent_notification(saved_search, EmailType.AGENT_ASSIGNMENT,
                                 AgentMessages.AGENT_ASSIGNMENT_ALL_MESSAGE, emails)
        _send_admin_notification(saved_search, EmailType.AGENT_ASSIGNMENT,
                                 AdminMessages.AGENT_ASSIGNMENT_MESSAGE)

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["put"], name="Update Frequency")
    def update_email_notif_frequency(self, request, pk=None):
        frequency = request.data.get("frequency", None)
        queryset = self.get_queryset()
        try:
            saved_search = queryset.get(pk=int(pk))
            if frequency:
                saved_search.frequency = frequency
                saved_search.save()
        except UserSavedSearch.DoesNotExist:
            return Response(
                {"detail": "Saved Search does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = self.get_serializer(saved_search).data
        return Response(data, status=status.HTTP_200_OK)

    # @action(
    #     detail=False,
    #     methods=["get"],
    #     permission_classes=(IsAuthenticated, IsUserManager),
    # )
    # def all_saved_search(self, *args, **kwargs):
    #     queryset = self.get_queryset()

    #     serializer = ListUserSavedSearchWitahAdminSerializer(queryset, many=True)
    #     response = Response(serializer.data)
    #     return response


class FrequentlyAskedQuestionViewSet(viewsets.ModelViewSet, DestroyArchiveModelMixin):

    serializer_class = FrequentlyAskedQuestionSerializer
    queryset = FrequentlyAskedQuestion.objects.all()


class PropertyInquiryViewSet(viewsets.ModelViewSet):

    serializer_class = PropertyInquirySerializer
    queryset = PropertyInquiry.objects.all()

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            defaults = {**request.data, "user": request.user.id}
        else:
            defaults = {**request.data}
        serializer = self.get_serializer(data=defaults)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        self.send_mail(serializer.instance)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=(IsAuthenticated, IsUserManager),
    )
    def get_user_property_inqury(self, request, *args, **kwargs):
        fk_email_id = self.request.query_params.get("fk_email_id", None)

        inquiries = PropertyInquiry.objects.filter(fk_email__id=fk_email_id)

        serializer = self.get_serializer(inquiries, many=True)
        response = Response(serializer.data)

        return response

    def send_mail(self, instance, *args, **kwargs):
        mail = HomeswiprMailer(
            subject="Property New Inquiry Notification!",
            recipient=config("SEARCH_EMAIL", default=""),
            text_template="inquiry/email/property_inquiry.txt",
            html_template="inquiry/email/property_inquiry.html",
            context={
                "first_name": instance.user.first_name
                if instance.user
                else instance.first_name,
                "last_name": instance.user.last_name
                if instance.user
                else instance.last_name,
                "email": instance.user.email if instance.user else instance.email,
                "phone_number": instance.user.phone_number
                if instance.user
                else instance.phone_number,
                "question": instance.question,
                "property_name": instance.inquired_property.related_address,
                "property_url": "https://homeswipr.ca/property"
                + "/{}".format(instance.inquired_property.id),
            },
        )
        mail.send_mail()


class PropertyManagementView(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class = FeedBackSerializer

    @action(detail=False, methods=["post", "get"])
    def send_mail(self, request, *args, **kwargs):
        email = request.data.get('email')
        name = request.data.get('name')
        message = request.data.get('message')

        if email and message:
            mail = HomeswiprMailer(
                subject="Property Management Lead",
                recipient="test@test123.com",
                text_template="homeswipr/email/email_property_management.txt",
                html_template="homeswipr/email/email_property_management.html",
                context={
                    "name": name,
                    "email": email,
                    "message": message,
                },
            )
            mail.send_mail()
            return Response({"success": True})
        else:
            return Response({"success": False, "email": email, "message": message, "error": "This field may not be blank."})


class AddressViewSet(viewsets.GenericViewSet):

    serializer_class = AddressCommunityCitySerializer
    queryset = Address.active_objects.all()
    pagination_class = AutoCompleteSetPagination

    @action(detail=False, methods=["get"])
    def community_list(self, *args, **kwargs):

        search_text = self.request.query_params.get(
            "search_text", ""
        )
        city = self.request.query_params.get(
            "city", ""
        )
        queryset = Address.objects.filter(
            community_name__startswith=search_text,
            city__icontains=city
        ).values("community_name", "city").annotate(
            Count("city")
        ).exclude(
            community_name=""
        ).order_by().distinct().values_list("community_name", flat=True)

        page = self.paginate_queryset(queryset)

        return Response(data=page, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def city_list(self, *args, **kwargs):

        search_text = self.request.query_params.get(
            "search_text", ""
        )
        # Vuetify combo box doesn't support dictionary yet
        queryset =  self.get_queryset().filter(
            city__startswith=search_text,
        ).exclude(
            community_name=""
        ).annotate(Count("city")).order_by("city").distinct().values_list("city", flat=True)

        page = self.paginate_queryset(queryset)

        return Response(data=page, status=status.HTTP_200_OK)

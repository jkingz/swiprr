import datetime
import decimal
import operator

from core.shortcuts import convert_query_params_to_boolean, get_object_or_403
from crea_parser.models import Parking, Property, PropertyInfo, PropertyPhoto
from crea_parser.submodels.metadata import PropertyPropertyType, PropertyTransactionType
from dateutil import parser
from ddf_manager.ddf_logger import logger
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Exists, F, OuterRef, Q, base
from django.db.models.functions import Coalesce
from functools import reduce
from rest_framework import filters

from .exceptions import (
    ParameterFormatTypeNotExpected,
)
from .models import UserSavedSearch


class PropertyHelperMixin(object):
    """
    A property mixin to properly implement DRY principle
    """

    def get_base_property(self):
        """
        Get property that has been select related
        """
        return Property.active_objects.prefetch_related(
            "Address", "Building", "Info", "land", "Photos", "Info__transaction_type",
            "Building__size_interior_unit"
        ).annotate(general_price=Coalesce("Info__price", "Info__lease"))

    def filter_valid_property(self, queryset):
        """
        Gets the property with valid property type.

        Property that is not land and etc
        """
        return queryset.filter(
            Info__property_type__in=PropertyPropertyType.get_valid_property_type_as_list()
        )

    def filter_property_by_keyword(self, queryset, search_text):
        # Searches the address, community name based on the search text
        return queryset.filter(
            Q(Address__address_line1__icontains=search_text)
            | Q(Address__address_line2__icontains=search_text)
            | Q(Address__street_number__icontains=search_text)
            | Q(Address__street_direction_prefix__icontains=search_text)
            | Q(Address__street_name__icontains=search_text)
            | Q(Address__street_suffix__icontains=search_text)
            | Q(Address__street_direction_suffix__icontains=search_text)
            | Q(Address__unit_number__icontains=search_text)
            | Q(Address__box_number__icontains=search_text)
            | Q(Address__city__icontains=search_text)
            | Q(Address__postal_code__icontains=search_text)
            | Q(Address__province__icontains=search_text)
            | Q(Address__community_name__icontains=search_text)
            | Q(Address__neighbourhood__icontains=search_text)
            | Q(Address__subdivision__icontains=search_text)
            | Q(Info__public_remarks__icontains=search_text)
        ).distinct()

    def check_format_type_decimal_or_bad_request(self, to_check, param_name):
        try:
            if type(to_check) == decimal:
                return to_check
            return decimal.Decimal(to_check)
        except decimal.InvalidOperation:
            raise ParameterFormatTypeNotExpected(
                param_name=param_name, var_type="Decimal"
            )

    def check_format_type_integer_or_bad_request(self, to_check, param_name):
        try:
            if type(to_check) == int:
                return to_check
            return int(to_check)
        except ValueError:
            raise ParameterFormatTypeNotExpected(
                param_name=param_name, var_type="Integer"
            )

    def check_format_type_date_or_bad_request(self, to_check, param_name):
        try:
            if isinstance(to_check, datetime.date):
                return to_check
            return parser.parse(to_check)
        except ValueError:
            raise ParameterFormatTypeNotExpected(param_name=param_name, var_type="Date")

    def construct_advance_search_parameters(self, saved_search_pk=None):
        # Constructs a dictionary from saved search from query parameters
        # Use saved search, if it is passed

        final_params = {}

        if saved_search_pk:
            saved_search = get_object_or_403(
                UserSavedSearch.active_objects, pk=saved_search_pk
            )
            final_params["search_text"] = saved_search.search_text
            final_params[
                "lower_boundary_price_range"
            ] = saved_search.lower_boundary_price_range
            final_params[
                "upper_boundary_price_range"
            ] = saved_search.upper_boundary_price_range
            final_params[
                "least_amount_of_bedroom"
            ] = saved_search.least_amount_of_bedroom
            final_params[
                "least_amount_of_bathroom"
            ] = saved_search.least_amount_of_bathroom
            final_params["ownership_type_ids"] = saved_search.ownership_type_ids
            final_params["transaction_type_id_list"] = saved_search.transaction_type_id_list
            final_params["community_list_search_text"] = saved_search.community_list_search_text
            final_params["has_video"] = saved_search.has_video
            final_params["city_list"] = saved_search.city_list
            final_params["from_creation_date"] = saved_search.from_creation_date
            final_params["until_creation_date"] = saved_search.until_creation_date
            final_params[
                "from_listing_contract_date"
            ] = saved_search.from_listing_contract_date
            final_params[
                "until_listing_contract_date"
            ] = saved_search.until_listing_contract_date
            final_params["parking_type_ids"] = saved_search.parking_type_ids
            final_params["zoning_keyword"] = saved_search.zoning_keyword
            final_params["year_built"] = saved_search.year_built
            final_params["year_built_condition"] = saved_search.year_built_condition
            final_params["size"] = saved_search.size
            final_params["building_type_list"] = saved_search.building_type_list
            final_params["has_garage"] = saved_search.has_garage
            final_params["basement_type_list"] = saved_search.basement_type_list
            final_params["has_suite"] = saved_search.has_suite
            final_params["architectural_style"] = saved_search.architectural_style
        else:
            final_params["search_text"] = self.request.query_params.get(
                "search_text", ""
            )
            final_params["lower_boundary_price_range"] = self.request.query_params.get(
                "lower_boundary_price_range", None
            )
            final_params["upper_boundary_price_range"] = self.request.query_params.get(
                "upper_boundary_price_range", None
            )
            final_params["least_amount_of_bedroom"] = self.request.query_params.get(
                "least_amount_of_bedroom", 0
            )
            final_params["least_amount_of_bathroom"] = self.request.query_params.get(
                "least_amount_of_bathroom", 0
            )
            final_params["ownership_type_ids"] = self.request.query_params.getlist(
                "ownership_type_ids[]", []
            )
            final_params["transaction_type_id_list"] = self.request.query_params.getlist(
                "transaction_type_id_list[]", None
            )
            final_params["community_list_search_text"] = self.request.query_params.getlist(
                "community_list_search_text[]", []
            )
            final_params["has_video"] = self.request.query_params.get("has_video", None)
            final_params["from_creation_date"] = self.request.query_params.get(
                "from_creation_date", None
            )
            final_params["until_creation_date"] = self.request.query_params.get(
                "until_creation_date", None
            )
            final_params["from_listing_contract_date"] = self.request.query_params.get(
                "from_listing_contract_date", None
            )
            final_params["city_list"] = self.request.query_params.getlist("city_list[]", [])
            final_params["until_listing_contract_date"] = self.request.query_params.get(
                "until_listing_contract_date", None
            )
            final_params["parking_type_ids"] = self.request.query_params.getlist(
                "parking_type_ids[]", []
            )
            final_params["zoning_keyword"] = self.request.query_params.get(
                "zoning_keyword", None
            )
            final_params["property_type"] = self.request.query_params.get(
                "property_type", ""
            )
            final_params["year_built"] = self.request.query_params.get(
                "year_built", None
            )
            final_params["size"] = self.request.query_params.get("size", "")
            final_params["building_type_list"] = self.request.query_params.getlist(
                "building_type_list[]", ""
            )
            final_params["year_built_condition"] = self.request.query_params.get(
                "year_built_condition", None
            )
            final_params["basement_type_list"] = self.request.query_params.getlist(
                "basement_type_list[]", ""
            )
            final_params["has_garage"] = self.request.query_params.get(
                "has_garage", None
            )
            final_params["has_suite"] = self.request.query_params.get("has_suite", None)
            final_params["size_unit_type"] = self.request.query_params.get("size_unit_type", None)
            final_params["architectural_style"] = self.request.query_params.getlist(
                "architectural_style[]", []
            )
            final_params["listing_type"] = self.request.query_params.get("listing_type", None)
        return final_params

    def load_other_section_page_filters(
        self, load_more_queryset, params, include_geo_location=True
    ):
        # This is the filters needed for the "More" user interface

        # If search_text text is passed get that first
        city = params.get("search_text", "")
        if self.action != "propz_houses":
            subquery = PropertyPhoto.objects.filter(connected_property=OuterRef("pk"))
            load_more_queryset = load_more_queryset.filter(Exists(subquery))

        # Override search_text with city if it's passed
        if params.get("city", ""):
            city = params.get("city", "")

        if city:
            load_more_queryset = load_more_queryset.filter(
                Q(Address__city__icontains=city)
            )

        if not city and include_geo_location:

            lng = self.request.query_params.get("lng", None)
            lat = self.request.query_params.get("lat", None)

            if lng is not None and lat is not None:
                user_coordinates = Point(float(lng), float(lat))
                load_more_queryset = load_more_queryset.filter(
                    Geo__coordinates__dwithin=(user_coordinates, 1),
                    Geo__coordinates__distance_lte=(user_coordinates, D(km=100)),
                ).annotate(distance=Distance("Geo__coordinates", user_coordinates))

        # Removes no photos on the front page
        # load_more_queryset = load_more_queryset.annotate(
        #     property_photo_count=Count('Photos')
        # ).exclude(property_photo_count=0)

        return load_more_queryset

    def advance_search(self, property_query_set, params):
        search_text = params.get("search_text", "")

        # Checks if the search_text is equals to a listing id number, if it is.
        # let the frontend know that it matches and return a mls match as true
        # NOTE: We used filter instead of get here. That the forontend will always
        # exepct the same data structure. Use property, here not the already
        # filtered queryset
        property_match = Property.active_objects.filter(listing_id=search_text).order_by(
            "pk"
        )

        if property_match and params.get("listing_type", None) == 1:
            self.mls_matched = True
            # Return property match queryset instead of searching
            # the whole property
            return property_match

        # NOTE: Remember that querysets are lazy!
        # These filters are not run until the queryset is evaluated

        # Price range part
        lower_boundary_price_range = params.get("lower_boundary_price_range", None)
        upper_boundary_price_range = params.get("upper_boundary_price_range", None)

        if lower_boundary_price_range and lower_boundary_price_range != 0:
            lower_boundary_price_range = self.check_format_type_decimal_or_bad_request(
                lower_boundary_price_range, "lower_boundary_price_range"
            )

            property_query_set = property_query_set.filter(
                general_price__gte=lower_boundary_price_range
            )

        if upper_boundary_price_range and upper_boundary_price_range != 0:
            upper_boundary_price_range = self.check_format_type_decimal_or_bad_request(
                upper_boundary_price_range, "upper_boundary_price_range"
            )
            property_query_set = property_query_set.filter(
                general_price__lte=upper_boundary_price_range
            )

        # Bedroom and bathroom part
        least_amount_of_bedroom = params.get("least_amount_of_bedroom", 0)

        if least_amount_of_bedroom:
            least_amount_of_bedroom = self.check_format_type_integer_or_bad_request(
                least_amount_of_bedroom, "least_amount_of_bedroom"
            )
            property_query_set = property_query_set.filter(
                Building__bedrooms_total__gte=least_amount_of_bedroom
            )

        least_amount_of_bathroom = params.get("least_amount_of_bathroom", 0)

        if least_amount_of_bathroom:
            least_amount_of_bathroom = self.check_format_type_integer_or_bad_request(
                least_amount_of_bathroom, "least_amount_of_bathroom"
            )
            property_query_set = property_query_set.filter(
                Building__bathroom_total__gte=least_amount_of_bathroom
            )

        # If an ownership type is passed
        ownership_type_ids = params.get("ownership_type_ids", [])
        if ownership_type_ids:

            for ownership_id in ownership_type_ids:
                ownership_id = self.check_format_type_integer_or_bad_request(
                    ownership_id, "ownership_ids"
                )

            property_query_set = property_query_set.filter(
                    Info__ownership_type__metadata_entry_id__in=ownership_type_ids
                )

        # If a transaction type is passed
        transaction_type_id_list = params.get("transaction_type_id_list", None)
        if transaction_type_id_list:
            property_query_set = property_query_set.filter(
                Info__transaction_type__metadata_entry_id__in=transaction_type_id_list
            )

        # If community search text is passed
        community_list_search_text = params.get("community_list_search_text", [])
        if community_list_search_text:

            # NOTE: This allows dynamic number of community to be filtered
            community_name_filter = reduce(operator.or_, (Q(Address__community_name__icontains = item) for item in community_list_search_text))
            neighbourhood_filter = reduce(operator.or_, (Q(Address__neighbourhood__icontains = item) for item in community_list_search_text))
            subdvision_filter = reduce(operator.or_, (Q(Address__subdivision__icontains = item) for item in community_list_search_text))

            property_query_set = property_query_set.filter(
                community_name_filter
                | neighbourhood_filter
                | subdvision_filter
            )

        # If city text is passed
        city_list = params.get("city_list", [])
        if city_list:
            city_list_filter = reduce(operator.or_, (Q(Address__city__icontains = item) for item in city_list))
            property_query_set = property_query_set.filter(
                city_list_filter
            )

        # If has_video is ticked
        has_video = params.get("has_video", None)
        if has_video is not None:
            has_video = convert_query_params_to_boolean(has_video)
            if has_video:
                property_query_set = property_query_set.exclude(
                    Q(alternate_url__video_link=None) | Q(alternate_url__video_link="")
                )

        # Creation date filters
        from_creation_date = params.get("from_creation_date", None)
        until_creation_date = params.get("until_creation_date", None)

        if from_creation_date:
            from_creation_date = self.check_format_type_date_or_bad_request(
                from_creation_date, "from_creation_date"
            )
            property_query_set = property_query_set.filter(
                creation_date__gte=from_creation_date
            )

        if until_creation_date:
            until_creation_date = self.check_format_type_date_or_bad_request(
                until_creation_date, "unil_creation_date"
            )

            property_query_set = property_query_set.filter(
                creation_date__lte=until_creation_date
            )

        # Listing Contract date filters
        from_listing_contract_date = params.get("from_listing_contract_date", None)
        until_listing_contract_date = params.get("until_listing_contract_date", None)

        if from_listing_contract_date and until_listing_contract_date:

            from_listing_contract_date = self.check_format_type_date_or_bad_request(
                from_listing_contract_date, "from_listing_contract_date"
            )
            until_listing_contract_date = self.check_format_type_date_or_bad_request(
                until_listing_contract_date, "until_listing_contract_date"
            )

            property_query_set = property_query_set.filter(
                Info__listing_contract_date__gte=from_listing_contract_date,
                Info__listing_contract_date__lte=until_listing_contract_date,
            )

        # Parking type filters
        parking_type_ids = params.get("parking_type_ids", [])

        if parking_type_ids:
            for parking_type_id in parking_type_ids:
                parking_type_id = self.check_format_type_integer_or_bad_request(
                    parking_type_id, "parking_type_ids"
                )

            property_query_set = property_query_set.filter(
                Parking__name__in=parking_type_ids
            )

        # Zoning Filters
        zoning_keyword = params.get("zoning_keyword", None)

        if zoning_keyword:
            property_query_set = property_query_set.filter(
                Info__zoning_description__icontains=zoning_keyword
            )

        # Property Type Filter
        property_type = params.get("property_type", None)

        if property_type:
            property_query_set = property_query_set.filter(
                Info__property_type__icontains=property_type
            )

        # Year Built filters
        year_built = params.get("year_built", None)

        if year_built:
            year_built_condition = params.get("year_built_condition", None)
            year_built = int(year_built)
            # check condition
            if year_built_condition == "exact":
                property_query_set = property_query_set.filter(
                    Building__constructed_date__year=year_built
                )
            elif year_built_condition == "before":
                property_query_set = property_query_set.filter(
                    Building__constructed_date__year__lte=year_built
                )
            elif year_built_condition == "after":
                property_query_set = property_query_set.filter(
                    Building__constructed_date__year__gte=year_built
                )
            else:
                property_query_set = property_query_set.filter(
                    Building__constructed_date__year__gte=year_built
                )

        # Size Filters
        size = params.get("size", None)
        size_unit_type = params.get("size_unit_type", None)
        if not size_unit_type and size:
            if size.isnumeric():
                property_query_set = property_query_set.filter(
                    Q(land__size_total__gte=size) |
                    Q(land__size_frontage__gte=size)
                )
            else:
                property_query_set = property_query_set.filter(
                    land__size_total_text__icontains=size
                )
        elif size and size_unit_type:
            property_query_set = property_query_set.filter(
                Q(land__size_total__gte=size) &
                Q(land__size_total_unit__metadata_entry_id__in=size_unit_type)
            )

        # Building Type Filters
        building_type_list = params.get("building_type_list", [])
        if building_type_list:
            property_query_set = property_query_set.filter(
                Building__model_type__metadata_entry_id__in=building_type_list
            )

        # Basement Type Filters
        basement_type = params.get("basement_type_list", None)
        if basement_type:
            property_query_set = property_query_set.filter(
                Building__basement_type__metadata_entry_id__in=basement_type
            )

        # Has Garage Filters
        has_garage = params.get("has_garage", None)
        if has_garage:
            if has_garage == "Garage":
                property_query_set = property_query_set.filter(
                    Q(Parking__name=1) |
                    Q(Parking__name=2) |
                    Q(Parking__name=3) |
                    Q(Parking__name=4) |
                    Q(Parking__name=37)
                )
            else:
                property_query_set = property_query_set.filter(
                    Q(Parking__name=13) |
                    Q(Parking__name=15)
                )

        # Has Suite Filters
        has_suite = params.get("has_suite", None)
        if has_suite:
            if has_suite == "Suite":
                property_query_set = property_query_set.filter(
                    Building__basement_features__metadata_entry_id=22
                )
            else:
                property_query_set = property_query_set.exclude(
                    Building__basement_features__metadata_entry_id=22
                )

        # Architectural Style
        architectural_style = params.get("architectural_style", None)
        if architectural_style:
            property_query_set = property_query_set.filter(
                Building__architectural_style__metadata_entry_id__in=architectural_style
            )

        # Listing Type Style
        listing_type = params.get("listing_type", None)
        if listing_type:
            property_query_set = property_query_set.filter(
                Info__listing_type=listing_type
            )

        return property_query_set


class FavoriteHelperMixin(object):
    """
    A favorite mixin to properly implement DRY principle
    """

    def filter_favorite_by_address(self, queryset, search_text):
        return queryset.filter(
            Q(favorited_property__Address__address_line1__icontains=search_text)
            | Q(favorited_property__Address__address_line1__icontains=search_text)
            | Q(favorited_property__Address__address_line2__icontains=search_text)
            | Q(favorited_property__Address__street_number__icontains=search_text)
            | Q(
                favorited_property__Address__street_direction_prefix__icontains=search_text
            )
            | Q(favorited_property__Address__street_name__icontains=search_text)
            | Q(favorited_property__Address__street_suffix__icontains=search_text)
            | Q(
                favorited_property__Address__street_direction_suffix__icontains=search_text
            )
            | Q(favorited_property__Address__unit_number__icontains=search_text)
            | Q(favorited_property__Address__box_number__icontains=search_text)
            | Q(favorited_property__Address__city__icontains=search_text)
            | Q(favorited_property__Address__postal_code__icontains=search_text)
            | Q(favorited_property__Address__province__icontains=search_text)
        )


class NullsLastOrderFilterMixin(filters.OrderingFilter):
    """
    Forces order filter in Django Rest Framework to tell Postgres
    to make null values last.
    """

    def filter_queryset(self, queryset):
        ordering = self.get_ordering(self.request, queryset, self)

        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == "-":
                    # If we detected a minus/negative sign only get the second element onwards.
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset

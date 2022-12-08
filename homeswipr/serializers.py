import datetime
import dateutil.parser
import math

from core.shortcuts import get_object_or_None
from core.utils import PropertyGeolocationManager, TimezoneManager
from crea_parser.models import (
    Address,
    AgentDetails,
    AlternateURL,
    Building,
    Business,
    Event,
    Geolocation,
    Land,
    OfficeDetails,
    Parking,
    Phone,
    Property,
    PropertyInfo,
    PropertyPhoto,
    Room,
    Utility,
    Website,
)
from crea_parser.submodels.metadata import (
    PropertyTransactionType,
    PropertyPropertyType,
    PropertyArchitecturalStyle,
    PropertyBuildingType,
    PropertyMeasureUnit,
    PropertyRoomType,
    PropertyRoomLevel,
    PropertyFeature,
    PropertyFoundationType,
    PropertyStorageType,
    PropertyStructureType,
)
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.formats import number_format
from rest_framework import serializers
from users.models import HomeswiprLead, User
from users.serializers import UserProfileSerializer

from .models import (
    AgentFavorite,
    FrequentlyAskedQuestion,
    PropertyFavorite,
    PropertyInquiry,
    UserSavedSearch,
    Brokerage,
    Agent,
    LawFirm
)


class BrokerageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brokerage
        fields = '__all__'


class RealtorAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'


class LawFirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawFirm
        fields = '__all__'


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        #  TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        #  TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class OfficeDetailsSerializer(serializers.ModelSerializer):

    Phone = PhoneSerializer(many=True)
    website = WebsiteSerializer(many=True, read_only=True)

    class Meta:
        model = OfficeDetails
        #  TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class AgentSerializer(serializers.ModelSerializer):

    Office = OfficeDetailsSerializer(read_only=True)
    Phone = PhoneSerializer(many=True, read_only=True)
    website = WebsiteSerializer(many=True, read_only=True)

    class Meta:
        model = AgentDetails
        #  TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class PropertyPhotoSerializer(serializers.ModelSerializer):
    media_url = serializers.ReadOnlyField()

    class Meta:
        #  TODO: Specify fields in the future once UI is defined
        model = PropertyPhoto

        fields = ("media_url", "thumbnail_url", "photo_url")


class PropertyInfoSerializer(serializers.ModelSerializer):

    price = serializers.DecimalField(102, 2)
    lease = serializers.SerializerMethodField("lease_localize")
    previous_price = serializers.SerializerMethodField(
        "previous_price_localize"
    )
    previous_lease = serializers.SerializerMethodField(
        "previous_lease_localize"
    )
    listing_age = serializers.SerializerMethodField()

    lease_per_time_display = serializers.ReadOnlyField()
    transaction_type_display = serializers.ReadOnlyField()
    features_display = serializers.ReadOnlyField()
    ownership_type_display = serializers.ReadOnlyField()
    pool_features_display = serializers.ReadOnlyField()
    pool_type_display = serializers.ReadOnlyField()
    property_type_display = serializers.ReadOnlyField()
    storage_type_display = serializers.ReadOnlyField()
    structure_display = serializers.ReadOnlyField()
    view_type_display = serializers.ReadOnlyField()
    maintenance_fee_type_display = serializers.ReadOnlyField()

    class Meta:
        model = PropertyInfo
        fields = "__all__"
        read_only_fields = (
            "date_created", "date_updated", "listing_type",
            "ListingID", "connected_property", "amenities_near_by",
            "communication_type", "community_features", "crop",
            "document_type", "easement", "equipment_type",
            "features", "farm_type", "irrigation_type",
            "live_stock_type", "loading_type", "machinery",
            "maintenance_fee_type", "pool_features", "pool_type",
            "rental_equipment_type", "right_type", "road_type",
            "sign_type", "storage_type", "structure",
            "view_type", "storage_type", "structure",
            "maintenance_fee_type_display"
        )

    def previous_price_localize(self, obj):
        if obj.previous_price:
            return number_format(math.trunc(obj.previous_price))
        else:
            return None

    def previous_lease_localize(self, obj):
        if obj.previous_lease:
            return number_format(math.trunc(obj.previous_lease))
        else:
            return None

    def price_localize(self, obj):
        # Localize decimal price, adds comma and makes
        # it a whole number
        if obj.price:
            return number_format(math.trunc(obj.price))
        else:
            return None

    def lease_localize(self, obj):
        # Localize decimal price, adds comma and makes
        # it a whole number
        lease_price = obj.lease
        if lease_price:
            return number_format(math.trunc(lease_price))
        else:
            return None

    def get_listing_age(self, obj):
        # Calculate date difference upon listing date.
        listing_age = None
        listing_date = obj.listing_contract_date
        current_date = timezone.localtime()
        date_created = obj.date_created

        if listing_date:
            listing_age = (current_date - listing_date).days
        else:
            listing_age = (current_date - date_created).days

        return listing_age


class AddressSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    street_address = serializers.CharField()
    address_line2 = serializers.CharField()

    class Meta:
        #  TODO: Specify fields in the future once UI is defined
        model = Address
        fields = "__all__"
        read_only_fields = (
            "ListingID", "connected_property", "amenities_near_by",
            "communication_type", "community_features", "crop",
            "document_type", "easement", "equipment_type", "features",
            "farm_type", "irrigation_type", "live_stock_type", "loading_type",
            "machinery", "maintenance_fee_type", "pool_features",
            "pool_type", "rental_equipment_type", "right_type", "road_type",
            "sign_type", "storage_type", "structure", "view_type", "date_created", "date_updated"
        )

    def get_city(self, obj):
        # The .title() used here is a python built in String method
        # to return a titlecased version of the string.
        return obj.city.title()

    def get_street_address(self, obj):
        # The .title() used here is a python built in String method
        # to return a titlecased version of the string.
        return obj.street_address.title()

    def get_address_line2(self, obj):
        # The .title() used here is a python built in String method
        # to return a titlecased version of the string.
        return obj.address_line2.title()


class RoomSerializer(serializers.ModelSerializer):

    model_type_display = serializers.ReadOnlyField()
    level_display = serializers.ReadOnlyField()

    class Meta:
        model = Room
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class BuildingSerializer(serializers.ModelSerializer):

    size_interior_display = serializers.ReadOnlyField()
    appliances_display = serializers.ReadOnlyField()
    architectural_style_display = serializers.ReadOnlyField()
    basement_features_display = serializers.ReadOnlyField()
    constructed_date_display = serializers.ReadOnlyField()
    exterior_finish_display = serializers.ReadOnlyField()
    flooring_type_display = serializers.ReadOnlyField()
    foundation_type_display = serializers.ReadOnlyField()
    roof_material_display = serializers.ReadOnlyField()
    roof_style_display = serializers.ReadOnlyField()
    utility_water_display = serializers.ReadOnlyField()
    model_type_display = serializers.ReadOnlyField()
    basement_type_display = serializers.ReadOnlyField()

    class Meta:
        model = Building
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"
        read_only_fields = (
            "connected_property", "amenities",
            "amperage", "appliances", "architectural_style",
            "basement_development", "basement_features", "basement_type", "ceiling_type",
            "clear_ceiling_height", "construction_material", "cooling_type", "exterior_finish",
            "fireplace_type", "fire_protection", "fixture",
            "flooring_type", "foundation_type", "heating_fuel", "heating_type",
            "roof_material", "roof_style", "store_front", "model_type", "utility_power", "utility_water",
            "date_created", "date_updated", "fireplace_fuel", "basement_type_display"
        )


class LandSerializer(serializers.ModelSerializer):

    size_total_display = serializers.ReadOnlyField()
    fence_type_display = serializers.ReadOnlyField()
    landscape_features_display = serializers.ReadOnlyField()
    sewer_display = serializers.ReadOnlyField()

    class Meta:
        model = Land
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class AlternateURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateURL
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class GeolocationSerializer(serializers.ModelSerializer):
    lat = serializers.ReadOnlyField()
    lng = serializers.ReadOnlyField()

    class Meta:
        model = Geolocation
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class DashboardVideoURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternateURL
        # TODO: Specify fields in the future once UI is defined
        fields = ("video_link",)


class DashboardPhotosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PropertyPhoto
        fields = ("thumbnail_url", "media_url", "photo_url")


class DashboardInfoSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField("price_localize")
    lease = serializers.SerializerMethodField("lease_localize")
    previous_price = serializers.SerializerMethodField(
        "previous_price_localize"
    )
    previous_lease = serializers.SerializerMethodField(
        "previous_lease_localize"
    )
    listing_age = serializers.SerializerMethodField()
    transaction_type_display = serializers.ReadOnlyField()

    class Meta:
        model = PropertyInfo
        fields = (
            "transaction_type_display", "price", "lease",
            "previous_price", "previous_lease", "listing_age",
            "transaction_type_display", "lease_per_time_display"
        )

    def previous_price_localize(self, obj):
        if obj.previous_price:
            return number_format(math.trunc(obj.previous_price))
        else:
            return None

    def previous_lease_localize(self, obj):
        if obj.previous_lease:
            return number_format(math.trunc(obj.previous_lease))
        else:
            return None

    def price_localize(self, obj):
        # Localize decimal price, adds comma and makes
        # it a whole number
        if obj.price:
            return number_format(math.trunc(obj.price))
        else:
            return None

    def lease_localize(self, obj):
        # Localize decimal price, adds comma and makes
        # it a whole number
        lease_price = obj.lease
        if lease_price:
            return number_format(math.trunc(lease_price))
        else:
            return None

    def get_listing_age(self, obj):
        # Calculate date difference upon listing date.
        listing_age = None
        listing_date = obj.listing_contract_date
        current_date = timezone.localtime()
        date_created = obj.date_created

        if listing_date:
            listing_age = (current_date - listing_date).days
        else:
            listing_age = (current_date - date_created).days

        return listing_age


class DashboardAddressSerializer(serializers.ModelSerializer):

    city = serializers.SerializerMethodField()
    street_address = serializers.SerializerMethodField()
    address_line2 = serializers.SerializerMethodField()

    class Meta:
        #  TODO: Specify fields in the future once UI is defined
        model = Address
        fields = ("street_address", "address_line2", "city", "province")

    def get_city(self, obj):
        # The .title() used here is a python built in String method
        # to return a titlecased version of the string.
        return obj.city.title()

    def get_street_address(self, obj):
        # The .title() used here is a python built in String method
        # to return a titlecased version of the string.
        return obj.street_address.title()

    def get_address_line2(self, obj):
        # The .title() used here is a python built in String method
        # to return a titlecased version of the string.
        return obj.address_line2.title()


class DashboardBuildingSerializer(serializers.ModelSerializer):

    size_interior_display = serializers.ReadOnlyField()

    class Meta:
        model = Building
        # TODO: Specify fields in the future once UI is defined
        fields = ("size_interior_display", "bedrooms_total", "bathroom_total")


class DashboardOfficeDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfficeDetails
        #  TODO: Specify fields in the future once UI is defined
        fields = ("name",)


class DashboardAgentSerializer(serializers.ModelSerializer):

    Office = DashboardOfficeDetailsSerializer(read_only=True)
    class Meta:
        model = AgentDetails
        #  TODO: Specify fields in the future once UI is defined
        fields = ("Office",)


class PropertySerializer(serializers.ModelSerializer):

    Address = DashboardAddressSerializer(read_only=True)
    Photos = DashboardPhotosSerializer(many=True, read_only=True)
    Info = DashboardInfoSerializer(read_only=True)
    Geo = GeolocationSerializer(read_only=True)
    alternate_url = DashboardVideoURLSerializer(read_only=True)
    Agent = DashboardAgentSerializer(many=True, read_only=True)
    Building = DashboardBuildingSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorite_instance_pk = serializers.SerializerMethodField()
    booking_status = serializers.SerializerMethodField()
    created_by_user = UserProfileSerializer(required=False, read_only=True, source="created_by")

    class Meta:
        model = Property
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"
        read_only_fields = (
            "date_created", "date_updated", "listing_type", "created_by"
        )

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(PropertySerializer, self).to_representation(instance)

        data.update({
            'date_created':TimezoneManager.localize_to_canadian_timezone(instance.date_created),
            'date_updated': TimezoneManager.localize_to_canadian_timezone(instance.date_updated)
        })
        return data

    def get_is_favorited(self, instance):
        if self.context["request"].user.is_authenticated:
            exists = get_object_or_None(
                PropertyFavorite.active_objects,
                user=self.context["request"].user,
                favorited_property=instance,
            )
            if exists:
                return True
        return False

    def get_favorite_instance_pk(self, instance):
        # Get the favorite pk to reuse the  delete api
        # on favorite viewset
        if self.context["request"].user.is_authenticated:
            favorite_instance = get_object_or_None(
                PropertyFavorite.active_objects,
                user=self.context["request"].user,
                favorited_property=instance,
            )
            if favorite_instance:
                return favorite_instance.pk
        return None

    def get_booking_status(self, instance):
        # Property identifier if is booked by the logged user
        if self.context["request"].user.is_authenticated:
            user = self.context.get("request").user
            booking = instance.booked_property.filter(booking_client__user__id=user.id)
            if booking:
                return {
                    "is_approved": booking[0].is_approved,
                    "is_pending": booking[0].is_pending,
                    "is_cancel": True if booking[0].date_canceled else False,
                }
        return None


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class EventSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Event
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parking
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class UtilitySerializer(serializers.ModelSerializer):

    model_type_display = serializers.ReadOnlyField()

    class Meta:
        model = Utility
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"


class PropertyExpandedSerializer(serializers.ModelSerializer):
    # we changed it to expanded as a term as we are using many fields here
    # and it is no longer only for reading but also writing

    Address = AddressSerializer()
    Info = PropertyInfoSerializer()
    Building = BuildingSerializer()
    alternate_url = AlternateURLSerializer(read_only=True)
    land = LandSerializer(read_only=True)
    Geo = GeolocationSerializer(read_only=True)

    Photos = PropertyPhotoSerializer(many=True, read_only=True)
    Room = RoomSerializer(many=True, read_only=True)
    business_set = BusinessSerializer(many=True, read_only=True)
    events = EventSerialzier(many=True, read_only=True)
    Agent = AgentSerializer(many=True, read_only=True)
    Parking = ParkingSerializer(many=True, read_only=True)
    utility = UtilitySerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorite_instance_pk = serializers.SerializerMethodField()
    is_authenticated = serializers.SerializerMethodField()

    class Meta:
        model = Property
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"

    def get_is_favorited(self, instance):

        if self.context["request"].user.is_authenticated:
            exists = get_object_or_None(
                PropertyFavorite.active_objects,
                user=self.context["request"].user,
                favorited_property=instance,
            )

            if exists:
                return True
        return False

    def get_is_authenticated(self, instance):
        return self.context["request"].user.is_authenticated

    def get_favorite_instance_pk(self, instance):
        # Get the favorite pk to reuse the  delete api
        # on favorite viewset
        if self.context["request"].user.is_authenticated:
            favorite_instance = get_object_or_None(
                PropertyFavorite.active_objects,
                user=self.context["request"].user,
                favorited_property=instance,
            )
            if favorite_instance:
                return favorite_instance.pk
        return None

    def create(self, validated_data):
        validated_data_address = validated_data.get('Address', None)
        validated_data_info = validated_data.get('Info', None)
        validated_data_building = validated_data.get('Building', None)

        initial_data_geolocation = self.initial_data.get('Geolocation', None)
        initial_data_land = self.initial_data.get('land', None)
        initial_data_room = self.initial_data.get('Room', None)
        initial_data_agent = self.initial_data.get('Agent', None)
        initial_data_info = self.initial_data.get('Info', None)
        initial_data_building = self.initial_data.get('Building', None)

        request_user = self.context["request"].user
        try:
            property_instance = Property.objects.create(
                listing_type=2,
                created_by=self.context["request"].user
            )

            # Property Address
            address_instance = Address.objects.create(
                connected_property = property_instance,
                street_address=validated_data_address.get("street_address", ""),
                address_line1=validated_data_address.get("address_line1", ""),
                address_line2=validated_data_address.get("address_line2", ""),
                city=validated_data_address.get("city", ""),
                province=validated_data_address.get("province", ""),
                postal_code=validated_data_address.get("postal_code", ""),
                community_name=validated_data_address.get("community_name", ""),
                neighbourhood=validated_data_address.get("neighbourhood", ""),
            )

            # PropertyInfo
            info_instance = PropertyInfo.objects.create(
                connected_property=property_instance,
                listing_type=2,
                property_type=validated_data_info.get("property_type", None),
                price=validated_data_info.get("price", 0),
                transaction_type=validated_data_info.get("transaction_type", None),
                public_remarks=validated_data_info.get("public_remarks", None),
            )

            if initial_data_info.get("features", None):
                features = initial_data_info.get("features", None)
                info_instance.features.set(features)

            if initial_data_info.get("storage_type", None):
                storage_types = initial_data_info.get("storage_type", None)
                info_instance.storage_type.set(storage_types)

            if initial_data_info.get("structure", None):
                structures = initial_data_info.get("structure", None)
                info_instance.structure.set(structures)

            info_instance.save()

            # Building
            building_instance = Building.objects.create(
                connected_property=property_instance,
                bathroom_total=validated_data_building.get("bathroom_total", 0),
                bedrooms_total=validated_data_building.get("bedrooms_total", 0),
                bedrooms_above_ground=validated_data_building.get("bedrooms_above_ground", 0),
                bedrooms_below_ground=validated_data_building.get("bedrooms_below_ground", 0),
                constructed_date=validated_data_building.get("constructed_date", None),
                size_interior=validated_data_building.get("size_interior", None),
            )

            try:
                model_type_choice = PropertyBuildingType.objects.get(id=initial_data_building.get("model_type", None))
                building_instance.model_type.add(model_type_choice)
            except Building.DoesNotExist:
                raise serializers.ValidationError("Building Type can't be found.")
            
            architectural_style_choices = initial_data_building.get("architectural_style", None)
            if architectural_style_choices:
                building_instance.architectural_style.set(architectural_style_choices)

            try:
                size_interior_unit_choice = PropertyMeasureUnit.objects.get(id=initial_data_building.get("size_interior_unit", None))
                building_instance.size_interior_unit = size_interior_unit_choice
            except PropertyMeasureUnit.DoesNotExist:
                raise serializers.ValidationError("Property Measurement unit can't be found.")

            if initial_data_building.get("foundation_type", None):
                foundation_types = initial_data_building.get("foundation_type", None)
                building_instance.foundation_type.set(foundation_types)

            building_instance.save()

            # Get Geolocation if available
            request_result, request_made = PropertyGeolocationManager.add_geolocation(property_instance, address_instance)

            # If Geolocation has been sent by frontend
            if initial_data_geolocation.get('longitude', None) and initial_data_geolocation.get('latitude', None):
                coordinates = Point(
                    float(initial_data_geolocation.get('longitude', None)),
                    float(initial_data_geolocation.get('latitude', None))
                )

                # Create geolocation
                Geolocation.objects.get_or_create(
                    connected_property=property_instance,
                    coordinates=coordinates
                )

            # Land
            land = Land.objects.create(
                connected_property=property_instance,
                size_total=initial_data_land.get("size_total", None),
            )

            try:
                size_total_unit_choice = PropertyMeasureUnit.objects.get(pk=initial_data_land.get("size_total_unit", None))
                land.size_total_unit = size_total_unit_choice
                land.save()
            except PropertyMeasureUnit.DoesNotExist:
                raise serializers.ValidationError("Property Measurement unit can't be found.")

            # Room
            if initial_data_room.get('model_type', None) and initial_data_room.get('level', None) and initial_data_room.get('dimension', None):
                count = 0
                model_type = initial_data_room.get('model_type', None)
                level = initial_data_room.get('level', None)

                for index in model_type:
                    try:
                        model_type = PropertyRoomType.objects.get(pk=model_type[count])
                    except PropertyMeasureUnit.DoesNotExist:
                        raise serializers.ValidationError("Property Room Type can't be found.")

                    try:
                        level = PropertyRoomLevel.objects.get(pk=level[count])
                    except PropertyRoomLevel.DoesNotExist:
                        raise serializers.ValidationError("Property Room Type can't be found.")

                    if model_type and level:
                        Room.objects.create(
                            connected_property=property_instance,
                            model_type=model_type,
                            level=level,
                            dimension=initial_data_room.get('dimension', None)[count]
                        )
                        count = count + 1

            # Set Agent
            if request_user and request_user.is_agent:
                name = request_user.first_name + " " + request_user.last_name
                agent = AgentDetails.objects.create(
                    name=name,
                    connected_property=property_instance
                )

                if request_user.phone_number:
                    Phone.objects.create(
                        text=request_user.phone_number,
                        agent=agent
                    )

            elif request_user and (request_user.is_user_manager or request_user.is_superuser) and initial_data_agent:
                if initial_data_agent:
                    for new_agent in initial_data_agent:
                        phone_number = new_agent.get('phone_number', None)

                        agent = AgentDetails.objects.create(
                            name=new_agent.get('name', None),
                            connected_property=property_instance
                        )

                        if phone_number:
                            Phone.objects.create(text=phone_number,agent=agent)
        except Exception as e:
            raise serializers.ValidationError(f'Issue encountered: {e}')

        return property_instance


class AddressAutoCompleteSerializer(serializers.ModelSerializer):

    Address = AddressSerializer(read_only=True)

    full_address = serializers.CharField(max_length=255)

    class Meta:
        model = Property
        # TODO: Specify fields in the future once UI is defined
        fields = ("Address", "full_address")


class PropertyFavoriteSerializer(serializers.ModelSerializer):

    favorite_type = serializers.CharField(default="Property", read_only=True)
    full_address = serializers.CharField(
        source="favorited_property.related_address", read_only=True
    )
    favorited_property = PropertySerializer(read_only=True)
    date_created = serializers.DateTimeField(
        format="%B %d,%Y", input_formats=["%B %d,%Y", "iso-8601"]
    )
    date_updated = serializers.DateTimeField(
        format="%B %d,%Y", input_formats=["%B %d,%Y", "iso-8601"]
    )

    class Meta:
        model = PropertyFavorite
        fields = (
            "full_address",
            "favorite_type",
            "favorited_property",
            "user",
            "date_created",
            "date_updated",
        )
        read_only_fields = (
            "full_address",
            "favorite_type",
            "favorited_property",
            "user",
            "date_created",
            "date_updated",
        )


class CreatePropertyFavoriteSerializer(serializers.ModelSerializer):
    # Separated due to how the other serializer handles favorited property.

    user = serializers.PrimaryKeyRelatedField(
        required=False, queryset=get_user_model().active_objects.all()
    )

    class Meta:
        model = PropertyFavorite
        fields = ("favorited_property", "user", "pk")
        read_only_fields = ("pk",)
        # Removes a default "unique together" constraint otherwise the whole serializer won't go
        # in our custom seriliazer.valdiate
        validators = []

    def validate(self, data):
        """
        putting owner since we didn't pass owner on the first initalization of data
        """
        data["user"] = self.context.get("request").user
        # Custom check for unique constraints before postgres throws an unexpected error
        exists = get_object_or_None(
            PropertyFavorite.active_objects,
            user=data.get("user", None),
            favorited_property=data.get("favorited_property", None),
        )

        if exists:
            raise serializers.ValidationError(
                "user with favorited_property already exists"
            )

        return super().validate(data)


class AgentFavoriteSerializer(serializers.ModelSerializer):

    favorite_type = serializers.CharField(default="Agent", read_only=True)
    name = serializers.CharField(source="favorited_agent.name", read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        required=False, queryset=get_user_model().active_objects.all()
    )

    class Meta:
        model = AgentFavorite
        fields = ("name", "favorite_type", "favorited_agent", "user")

        # Removes a default "unique together" constraint otherwise the whole serializer won't go
        # in our custom seriliazer.valdiate
        validators = []

    def validate(self, data):
        """
        putting owner since we didn't pass owner on the first initalization of data
        """
        data["user"] = self.context.get("request").user

        # Custom check for unique constraints before postgres throws an unexpected error
        exists = get_object_or_None(
            AgentFavorite.active_objects,
            user=data.get("user", None),
            favorited_agent=data.get("favorited_agent", None),
        )

        if exists:
            raise serializers.ValidationError(
                "user with favorited_agent already exists"
            )

        return super().validate(data)


class UserSavedSearchSerializer(serializers.ModelSerializer):

    from_admin_view = False

    user = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=get_user_model().active_objects.all(),
        default=serializers.CurrentUserDefault(),
        allow_null=True,
    )
    ownership_types = serializers.SerializerMethodField()
    parking_types = serializers.SerializerMethodField()
    transaction_type = serializers.SerializerMethodField()
    community_list_search_text_display = serializers.ReadOnlyField()
    city_list_display = serializers.ReadOnlyField()
    building_type_list_display = serializers.ReadOnlyField()
    basement_type_list_display = serializers.ReadOnlyField()

    class Meta:
        model = UserSavedSearch
        fields = (
            "title",
            "search_text",
            "city_list",
            "city_list_display",
            "zoning_keyword",
            "lower_boundary_price_range",
            "upper_boundary_price_range",
            "least_amount_of_bedroom",
            "least_amount_of_bathroom",
            "transaction_type_id_list",
            "transaction_type",
            "building_type_list",
            "building_type_list_display",
            "ownership_type_ids",
            "parking_type_ids",
            "community_list_search_text",
            "community_list_search_text_display",
            "has_video",
            "year_built",
            "year_built_condition",
            "size",
            "from_creation_date",
            "until_creation_date",
            "user",
            "from_listing_contract_date",
            "until_listing_contract_date",
            "created_by",
            "pk",
            "ownership_types",
            "parking_types",
            "has_garage",
            "basement_type_list",
            "basement_type_list_display",
            "has_suite",
            "architectural_style",
            "agents",
            "frequency"
        )
        read_only_fields = ("pk", "created_by")

    def get_transaction_type(self, obj):
        transaction_type = get_object_or_None(PropertyTransactionType.active_objects, pk=obj.transaction_type_id)
        if transaction_type:
            return transaction_type.short_value
        return None

    def get_ownership_types(self, obj):
        if obj.get_ownership_type_ids_display():
            return ", ".join(obj.get_ownership_type_ids_display())
        else:
            return ""

    def get_parking_types(self, obj):
        if obj.get_parking_type_ids_display():
            return ", ".join(obj.get_parking_type_ids_display())
        else:
            return ""

    def pre_save_handle_user(self, validated_data, instance=None):
        if not self.from_admin_view:
            # No point of passing the user if not admin, we must not pass
            # update a user, if not from admin view
            validated_data.pop("user", None)
            if instance is None:
                # If a new one, update the user
                validated_data["user"] = self.context.get("request").user
        elif self.from_admin_view:
            user_is_passed = validated_data.get("user", None)
            # If user is passed and from admin, view, keep it
            # IF NOT, keep or make the requester as the user
            if not user_is_passed and not instance:
                validated_data["user"] = self.context.get("request").user

        if not instance:
            validated_data["created_by"] = self.context.get("request").user
        else:
            validated_data.pop("created_by", None)
            validated_data.pop("user", None)

        return validated_data

    def create(self, validate_data):
        return super().create(self.pre_save_handle_user(validate_data))

    def update(self, instance, validated_data):
        # TODO: Implement another way of updating data for Django Signals
        return super().update(
            instance, self.pre_save_handle_user(validated_data, instance)
        )

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(UserSavedSearchSerializer, self).to_representation(instance)
        agents = instance.agents.all()
        if agents:
            user = get_user_model().objects.filter(pk__in=agents).values('first_name', 'last_name', 'id', 'email')
            agents_list = list()
            for agent in user:
                agents_list.append({
                    'pk': agent.get('id'),
                    'fullname': f"{agent.get('first_name')} {agent.get('last_name')}",
                    'email': agent.get('email')
                })
            data.update({'agents': agents_list})

        return data


class ListUserSavedSearchWitahAdminSerializer(UserSavedSearchSerializer):
    user = UserProfileSerializer()
    created_by = UserProfileSerializer()


class FrequentlyAskedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestion
        fields = "__all__"


class PropertyInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInquiry
        fields = "__all__"

    def validate_first_name(self, value):
        if not self.initial_data.get("user") and not value:
            raise serializers.ValidationError("This is field is required.")
        return value

    def validate_last_name(self, value):
        if not self.initial_data.get("user") and not value:
            raise serializers.ValidationError("This is field is required.")
        return value

    def validate_email(self, value):
        if (
            not self.initial_data.get("user")
            and not self.initial_data.get("phone_number")
            and not value
        ):
            raise serializers.ValidationError("This is field is required.")
        return value

    def validate_phone_number(self, value):
        if (
            not self.initial_data.get("user")
            and not self.initial_data.get("email")
            and not value
        ):
            raise serializers.ValidationError("This is field is required.")
        return value

    def validate(self, data):
        leads_detail = dict()

        user = data.get("user")
        if user:
            defaults = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
            }
            data.update(defaults)

        leads_detail.update(
            {
                "full_name": "{} {}".format(
                    data.get("first_name"), data.get("last_name")
                ),
                "email": data.get("email"),
                "phone_number": data.get("phone_number"),
            }
        )

        lead_instance = HomeswiprLead.objects.get_or_create(**leads_detail)[0]
        data.update({"fk_email": lead_instance})
        return data

    def to_representation(self, instance):
        """
        Customize get data response.
        """
        data = super(PropertyInquirySerializer, self).to_representation(instance)
        inquired_property = instance.inquired_property
        property_detail = dict()
        property_detail.update(
            {
                "ListingID": inquired_property.listing_id,
                "Address": "{} {}, {}".format(
                    inquired_property.Address.address_line1,
                    inquired_property.Address.city,
                    inquired_property.Address.province,
                ),
            }
        )
        data.update({"inquired_property": property_detail})
        return data

    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)


class FeedBackSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    subject = serializers.CharField(max_length=250)
    email = serializers.EmailField()
    message = serializers.CharField()


class AddressCommunityCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = (
            "community_name", "city"
        )


class PropertyOnlySerializer(serializers.ModelSerializer):
    # serializer to be used only for property model alone

    class Meta:
        model = Property
        # TODO: Specify fields in the future once UI is defined
        fields = "__all__"

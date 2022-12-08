import decimal

from core.models import CommonInfo
from core.shortcuts import get_object_or_None
from dateutil import parser
from ddf_manager.ddf_logger import logger
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models as geomodels
from django.db import models
from model_utils import FieldTracker

from crea_parser.submodels.metadata import (PropertyAccessType, PropertyAmenity, PropertyAmenityNearby, PropertyAmperage,
    PropertyAppliance, PropertyArchitecturalStyle, PropertyBasementDevelopment, PropertyBasementFeature, PropertyBasementType,
    PropertyBoard, PropertyBuildingType, PropertyBusinessSubType, PropertyBusinessType, PropertyCeilingType, PropertyClearCeilingHeight,
    PropertyCommunicationType, PropertyCommunityFeature, PropertyConstructionMaterial, PropertyConstructionStatus,
    PropertyConstructionStyleAttachment, PropertyConstructionStyleOther, PropertyConstructionStyleSplitLevel, PropertyCoolingType,
    PropertyCrop, PropertyCurrentUse, PropertyDocumentType, PropertyEasement, PropertyEquipmentType, PropertyExteriorFinish, PropertyFarmType,
    PropertyFeature, PropertyFenceType, PropertyFireProtection, PropertyFireplaceFuel, PropertyFireplaceType, PropertyFixture, PropertyFlooringType,
    PropertyFoundationType, PropertyFrontsOn, PropertyHeatingType, PropertyHeatingFuel, PropertyIrrigationType, PropertyLandDispositionType,
    PropertyLandscapeFeature, PropertyLeaseType, PropertyLiveStockType, PropertyLoadingType, PropertyMachinery, PropertyMaintenanceFeeType,
    PropertyMeasureUnit, PropertyOwnershipType, PropertyParkingType, PropertyPaymentUnit, PropertyPoolFeature, PropertyPoolType, PropertyPropertyType,
    PropertyRentalEquipmentType, PropertyRightType, PropertyRoadType, PropertyRoofMaterial, PropertyRoofStyle, PropertyRoomLevel, PropertyRoomType,
    PropertySewer, PropertySignType, PropertySoilEvaluationType, PropertySoilType, PropertyStorageType, PropertyStoreFront, PropertyStoreFront,
    PropertyStructureType, PropertySurfaceWater, PropertyTopographyType, PropertyTransactionType, PropertyUffiCode, PropertyUtilityPower,
    PropertyUtilityType, PropertyUtilityWater, PropertyViewType, PropertyWaterFrontType, PropertyZoningType, AgentIndividualDesignation,
    AgentLanguage, AgentSpecialtie, OfficeFranchisor, OfficeOrganizationType, OfficeOrganizationDesignation
)

# Django Models were created by a third party app to match the DDF design which is described under:
# https://www.crea.ca/wp-content/uploads/2016/02/Data_Distribution_Facility_Data_Feed_Technical_Documentation.pdf

# TODO: All the fields here are integrated with a third-party code ddf_manager, we really need to remap
# these fields!


class ConnectedToPropertyBaseModel(CommonInfo):
    """
    Should be inherited to all models that is connected to
    property.
    """

    class Meta:
        abstract = True

    @property
    def property_listing_id(self, *args, **kwargs):
        """
        Gets the listing id of the connected property
        """
        if hasattr(self, "connected_property") and self.connected_property:
            return self.connected_property.listing_id
        else:
            return "No Listing ID Found"

    @property
    def property_ddf_id(self, *args, **kwargs):
        """
        Gets the ddf id of the connected property
        """
        if hasattr(self, "connected_property") and self.connected_property:
            return self.connected_property.ddf_id
        else:
            return "No DDF ID Found"


class AgentConnectedBaseModel(CommonInfo):
    class Meta:
        abstract = True

    @property
    def property_listing_id(self, *args, **kwargs):
        """
        Gets the listing id of the connected property
        """
        listing_id = None

        if hasattr(self, "agent") and self.agent:
            listing_id = self.agent.connected_property.property_listing_id

        if not listing_id:
            if hasattr(self, "Office") and self.Office:
                listing_id = self.Office.property_listing_id

        if not listing_id:
            return "No Listing ID Found"
        return listing_id

    @property
    def property_ddf_id(self, *args, **kwargs):
        """
        Gets the ddf id of the connected property
        """
        ddf_id = None

        if hasattr(self, "agent") and self.agent:
            ddf_id = self.agent.connected_property.property_ddf_id

        if not ddf_id:
            if hasattr(self, "Office") and self.Office:
                ddf_id = self.Office.property_ddf_id

        if not ddf_id:
            return "No DDF ID Found"
        return ddf_id


class Property(CommonInfo):

    DDF = 1

    LISTING_TYPE = (
        (DDF, "DDF"),
    )

    ddf_id = models.TextField(blank=True, null=True, unique=True, default=None)
    listing_type = models.SmallIntegerField(choices=LISTING_TYPE, default=DDF)

    creation_date = models.DateTimeField(
        blank=True, null=True
    )

    last_updated = models.DateTimeField(
        blank=True, null=True
    )

    listing_id = models.CharField(max_length=225, blank=True)

    # Use a string import here to avoid recursive imports
    user_history = GenericRelation("users.UserHistory")

    created_by = models.ForeignKey('users.User', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Properties"

    def __str__(self, *args, **kwargs):
        return self.related_address

    @property
    def related_address(self, *args, **kwargs):
        address = get_object_or_None(Address, connected_property=self)
        title = f"{self.listing_id} - {self.ddf_id}"
        if address:
            title = f"{address.__str__()}"
        return f"{title}"

    @property
    def property_listing_id(self, *args, **kwargs):
        """
        NOTE: This is redundant for the property field but will make
        all the fields uniform on every model.
        """
        return self.listing_id

    @property
    def property_ddf_id(self, *args, **kwargs):
        """
        NOTE: This is redundant for the property field but will make
        all the fields uniform on every model.
        """
        return self.ddf_id


# Room is shared with DDF
class Room(ConnectedToPropertyBaseModel):

    # This is the room type
    # A special mapping is used here, to not shadow python type keyword while keeping
    # our sanity on maintaining the third party that was integrated on the system
    model_type = models.ForeignKey(
      PropertyRoomType, on_delete=models.PROTECT, related_name="room_type_set", null=True
    )

    width = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    width_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="room_width_set", null=True
    )

    length = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    length_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="room_length_set", null=True
    )

    level = models.ForeignKey(
      PropertyRoomLevel, on_delete=models.PROTECT, related_name="room_level_set", null=True
    )

    dimension = models.TextField(blank=True)

    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="Room", null=True
    )


    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    Type = models.TextField(blank=True)
    Width = models.TextField(blank=True)
    Length = models.TextField(blank=True)
    Level = models.TextField(blank=True)
    Dimension = models.TextField(blank=True)


    class Meta:
        verbose_name_plural = "Rooms"

    @property
    def model_type_display(self):
        if self.model_type:
            return self.model_type.short_value
        return None

    @property
    def level_display(self):
        if self.level:
            return self.level.short_value
        return None

    def __str__(self, *args, **kwargs):
        return f"{self.level} {self.model_type}"


class PropertyInfo(ConnectedToPropertyBaseModel):

    DDF = 1

    LISTING_TYPE = (
        (DDF, "DDF"),
    )


    ddf_id = models.TextField(blank=True, null=True, default=None)
    listing_id = models.CharField(max_length=225, blank=True)
    listing_type = models.SmallIntegerField(choices=LISTING_TYPE, default=DDF)
    last_updated = models.DateTimeField(
        blank=True, null=True
    )

    board = models.ForeignKey(
        PropertyBoard, on_delete=models.PROTECT, related_name="property_info_board_set", null=True
    )

    additional_information_indicator = models.TextField(blank=True)

    amenities_near_by = models.ManyToManyField(
       PropertyAmenityNearby, related_name="property_info_amenities_near_by_set"
    )

    communication_type = models.ManyToManyField(
      PropertyCommunicationType, related_name="property_info_communication_type_set"
    )

    community_features = models.ManyToManyField(
        PropertyCommunityFeature, related_name="property_info_community_features_set"
    )

    crop = models.ManyToManyField(
      PropertyCrop, related_name="property_info_crop_set"
    )

    document_type = models.ManyToManyField(
      PropertyDocumentType, related_name="property_info_document_type_set"
    )

    easement = models.ManyToManyField(
      PropertyEasement, related_name="property_info_easement_set"
    )

    equipment_type = models.ManyToManyField(
      PropertyEquipmentType, related_name="property_info_equipment_type_set"
    )

    features = models.ManyToManyField(
      PropertyFeature, related_name="property_info_features_set"
    )

    farm_type = models.ManyToManyField(
      PropertyFarmType, related_name="property_info_farm_type_set"
    )
    irrigation_type = models.ManyToManyField(
      PropertyIrrigationType, related_name="property_info_irrigation_type_set"
    )

    lease = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )
    lease_per_time = models.ForeignKey(
      PropertyPaymentUnit, on_delete=models.PROTECT, related_name="property_info_lease_per_time_set", null=True
    )

    lease_per_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="property_info_lease_per_unit_set", null=True
    )
    lease_term_remaining_freq = models.ForeignKey(
      PropertyPaymentUnit, on_delete=models.PROTECT, related_name="property_info_lease_term_remaining_freq_set", null=True
    )
    lease_term_remaining = models.TextField(blank=True)
    lease_type = models.ForeignKey(
      PropertyLeaseType,
      on_delete=models.PROTECT,
      related_name="property_info_lease_type_set",
      null=True
    )

    listing_contract_date = models.DateTimeField(blank=True, null=True)

    live_stock_type = models.ManyToManyField(
      PropertyLiveStockType,
      related_name="property_info_live_stock_type_set"
    )
    loading_type = models.ManyToManyField(
      PropertyLoadingType,
      related_name="property_info_loading_type_set"
    )

    location_description = models.TextField(blank=True)

    machinery = models.ManyToManyField(
      PropertyMachinery,
      related_name="property_info_machinery_set"
    )

    maintenance_fee =  models.DecimalField(
      max_digits=102, decimal_places=2, null=True, blank=True
    )
    maintenance_fee_payment_unit = models.TextField(
      blank=True
    )

    maintenance_fee_type = models.ManyToManyField(
      PropertyMaintenanceFeeType,
      related_name="property_info_maintenance_fee_type_set",
    )

    management_company = models.CharField(
      max_length=225,
      blank=True
    )

    more_information_link = models.CharField(
      max_length=225,
      blank=True
    )

    municipal_id = models.CharField(max_length=255, blank=True)

    ownership_type = models.ForeignKey(
      PropertyOwnershipType,
      on_delete=models.PROTECT,
      related_name="property_info_ownership_type_set",
      null=True
    )

    parking_space_total = models.CharField(max_length=255, blank=True)
    plan = models.CharField(max_length=255, blank=True)

    pool_features = models.ManyToManyField(
      PropertyPoolFeature,
      related_name="property_info_pool_features_set"
    )

    pool_type = models.ManyToManyField(
      PropertyPoolType,
      related_name="property_info_pool_type_set"
    )

    price = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )

    previous_price = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )
    previous_lease = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )

    price_per_unit = models.ForeignKey(
      PropertyPaymentUnit, on_delete=models.PROTECT, related_name="property_info_price_per_unit", null=True
    )

    property_type = models.ForeignKey(
      PropertyPropertyType, on_delete=models.PROTECT, related_name="property_info_property_type_set", null=True, blank=True,
    )
    public_remarks = models.TextField(blank=True)
    rental_equipment_type = models.ManyToManyField(
      PropertyRentalEquipmentType, related_name="property_info_rental_equipment_type_set"
    )

    right_type = models.ManyToManyField(
      PropertyRightType, related_name="property_info_right_type_set"
    )

    road_type = models.ManyToManyField(
      PropertyRoadType, related_name="property_info_road_type_set"
    )

    sign_type = models.ManyToManyField(
      PropertySignType, related_name="property_info_sign_type_set"
    )

    storage_type = models.ManyToManyField(
      PropertyStorageType, related_name="property_info_storage_type_set"
    )

    structure = models.ManyToManyField(
        PropertyStructureType, related_name="property_info_structure_set"
    )

    transaction_type = models.ForeignKey(
      PropertyTransactionType, on_delete=models.PROTECT, related_name="property_info_transaction_type_set", null=True
    )

    total_buildings = models.ForeignKey(
      PropertyBuildingType, on_delete=models.PROTECT, related_name="property_info_total_buildings_set", null=True
    )

    view_type = models.ManyToManyField(
      PropertyViewType, related_name="property_info_view_type_set"
    )

    water_front_type = models.ForeignKey(
      PropertyWaterFrontType, on_delete=models.PROTECT, related_name="property_info_water_front_type_set", null=True
    )

    water_front_name = models.CharField(max_length=255, blank=True)

    zoning_description = models.TextField(
      blank=True
    )

    zoning_type = models.ForeignKey(
       PropertyZoningType, on_delete=models.PROTECT, related_name="property_info_zoning_type_set", null=True
    )

    connected_property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="Info"
    )

    tracker = FieldTracker()

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    CONDO_STRATA = 1
    LEASEHOLD_CONDO_STRATA = 2
    FREE_HOLD = 3
    LEASEHOLD = 4
    TIMESHARE_FRACTIONAL = 5
    SHARES_COOPERATIVE = 6
    PARTIAL = 7
    UNKNOWN = 8
    UNDIVIDED_CO_OWNER_SHIP = 9
    LIFE_LEASE = 10
    FREE_HOLD_CONDO = 11
    STRATA = 12
    CONDO = 13
    COOP = 14
    OTHER_OWNERSHIP_TYPE = 15
    LEASE_HOLD_LAND = 16
    BARE_LAND_CONDO = 17

    OWNERSHIP_TYPE = (
        (CONDO_STRATA, "Condominium/Strata"),
        (LEASEHOLD_CONDO_STRATA, "Leasehold Condo/Strata"),
        (FREE_HOLD, "Freehold"),
        (LEASEHOLD, "Leasehold"),
        (TIMESHARE_FRACTIONAL, "Timeshare/Fractional"),
        (SHARES_COOPERATIVE, "Shares in Co-operative"),
        (PARTIAL, "Partial"),
        (UNKNOWN, "Unknown"),
        (UNDIVIDED_CO_OWNER_SHIP, "Undivided Co-ownership"),
        (LIFE_LEASE, "Life Lease"),
        (FREE_HOLD_CONDO, "Freehold Condo"),
        (STRATA, "Strata"),
        (CONDO, "Condominium"),
        (COOP, "Cooperative"),
        (OTHER_OWNERSHIP_TYPE, "Other, See Remarks"),
        (LEASE_HOLD_LAND, "Leasehold/Leased Land"),
        (BARE_LAND_CONDO, "Bare Land Condo"),
    )

    # These are the transaction type and their id constants that exists on crea
    FOR_SALE = 1
    FOR_RENT = 2
    FOR_LEASE = 3
    FOR_SALE_OR_FOR_RENT = 4

    TRANSACTION_TYPE = (
        (FOR_SALE, "For sale"),
        (FOR_RENT, "For rent"),
        (FOR_LEASE, "For lease"),
        (FOR_SALE_OR_FOR_RENT, "For sale or rent"),
    )

    # Real values for every transaction type
    FILTER_TRANSACTION_TYPE_VALUE = (
        (FOR_SALE, ["For sale", "For sale or rent"]),
        (FOR_RENT, ["For rent", "For sale or rent"]),
        (FOR_LEASE, ["For lease"]),
        (FOR_SALE_OR_FOR_RENT, ["For sale or rent", "For rent", "For sale"]),
    )

    # These are the property type and their id constants that exists on crea
    SINGLE_FAMILY = 300
    RECREATIONAL = 301
    AGRICULTURE = 302
    VACANT_LAND = 303
    OFFICE = 304
    RETAIL = 305
    BUSINESS = 306
    INDUSTRIAL = 307
    PARKING = 308
    SPECIAL_PURPOSE = 309
    MULTI_FAMILY = 310
    OTHER = 311
    HOSPITALITY = 312

    # We currently excludes the lands for property type
    VALID_PROPERTY_TYPE_IDS = [
        SINGLE_FAMILY,
        RECREATIONAL,
        OFFICE,
        RETAIL,
        BUSINESS,
        PARKING,
        SPECIAL_PURPOSE,
        MULTI_FAMILY,
        OTHER,
        HOSPITALITY,
    ]

    PROPERTY_TYPE = (
        (SINGLE_FAMILY, "Single Family"),
        (RECREATIONAL, "Recreational"),
        (AGRICULTURE, "Agriculture"),
        (VACANT_LAND, "Vacant Land"),
        (OFFICE, "Office"),
        (RETAIL, "Retail"),
        (BUSINESS, "Business"),
        (INDUSTRIAL, "Industrial"),
        (PARKING, "Parking"),
        (SPECIAL_PURPOSE, "Institutional - Special Purpose"),
        (MULTI_FAMILY, "Multi-family"),
        (OTHER, "Other"),
        (HOSPITALITY, "Hospitality"),
    )

    # NOTE: Fields are still camel case due to how parser inserts the field.
    # We need to change these when we overhaul the ddf manager

    ListingType = models.TextField(default="DDF")
    CreationDate = models.TextField(blank=True)  # Doesn't exist in DDF
    LastUpdated = models.TextField(blank=True)
    ListingID = models.TextField()
    Board = models.TextField(blank=True)
    AdditionalInformationIndicator = models.TextField(blank=True)
    AmmenitiesNearBy = models.TextField(blank=True)
    CommunicationType = models.TextField(blank=True)
    CommunityFeatures = models.TextField(blank=True)
    Crop = models.TextField(blank=True)
    DocumentType = models.TextField(blank=True)
    Easement = models.TextField(blank=True)
    EquipmentType = models.TextField(blank=True)
    Features = models.TextField(blank=True)
    FarmType = models.TextField(blank=True)
    IrrigationType = models.TextField(blank=True)
    Lease = models.TextField(blank=True)
    LeasePerTime = models.TextField(blank=True)
    LeasePerUnit = models.TextField(blank=True)
    LeaseTermRemainingFreq = models.TextField(blank=True)
    LeaseTermRemaining = models.TextField(blank=True)
    LeaseType = models.TextField(blank=True)

    # This is created through ddf manager (The integrated library), which is string. We should probably
    # update/refactor this one if we have the time. Since this is redundant
    ListingContractDate = models.TextField(blank=True)
    # NOTE: This and the top field is the same, we just change the variale type for querying
    formatted_listing_contract_date = models.DateField(
        blank=True, null=True
    )

    LiveStockType = models.TextField(blank=True)
    LoadingType = models.TextField(blank=True)
    LocationDescription = models.TextField(blank=True)
    Machinery = models.TextField(blank=True)
    MaintenanceFee = models.TextField(blank=True)
    MaintenanceFeePaymentUnit = models.TextField(blank=True)
    MaintenanceFeeType = models.TextField(blank=True)
    ManagementCompany = models.TextField(blank=True)
    MoreInformationLink = models.TextField(blank=True)
    MunicipalId = models.TextField(blank=True)

    # Choice like these needs to be refactored on ddf manager
    # and converted to be choice field on the database.
    OwnershipType = models.TextField(blank=True)

    ParkingSpaceTotal = models.TextField(blank=True)
    Plan = models.TextField(blank=True)
    PoolFeatures = models.TextField(blank=True)
    PoolType = models.TextField(blank=True)

    # This field is from the ddf manager (the library that was integrated to our system)
    # and should to be refactored when time is available
    # Remove this and refactor on ddf manager when we are 100% sure that the price field is within our expectation
    Price = models.TextField(blank=True)

    # Slowly try to make all field the proper naming on models
    # This is assumed that money doesn't go beyond $ 1 * 10^100 (Basically 99 zeroes with two decimals)
    decimal_price = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )
    decimal_lease = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )
    # previous_decimal_price = models.DecimalField(
    #     max_digits=102, decimal_places=2, null=True, blank=True
    # )
    # previous_decimal_lease = models.DecimalField(
    #     max_digits=102, decimal_places=2, null=True, blank=True
    # )

    PricePerUnit = models.TextField(blank=True)
    PropertyType = models.TextField(blank=True)
    PublicRemarks = models.TextField(blank=True)
    RentalEquipmentType = models.TextField(blank=True)
    RightType = models.TextField(blank=True)
    RoadType = models.TextField(blank=True)
    SignType = models.TextField(blank=True)
    StorageType = models.TextField(blank=True)
    Structure = models.TextField(blank=True)

    # Choice like these needs to be refactored on ddf manager
    # and converted to be choice field on the database.
    TransactionType = models.TextField(blank=True)

    TotalBuildings = models.TextField(blank=True)
    ViewType = models.TextField(blank=True)
    WaterFrontType = models.TextField(blank=True)
    WaterFrontName = models.TextField(blank=True)
    ZoningDescription = models.TextField(blank=True)
    ZoningType = models.TextField(blank=True)


    class Meta:
        verbose_name_plural = "Property Infos"

    @property
    def core_property_creation_date(self):
        return self.connected_property.creation_date

    @property
    def features_display(self):
        list_of_features = self.features.all().values_list("long_value", flat=True)
        return ', '.join(list_of_features)

    @property
    def pool_features_display(self):
        list_of_related_object = self.pool_features.active_objects.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def pool_type_display(self):
        list_of_related_object = self.pool_type.active_objects.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def property_type_display(self):
        if self.property_type:
            return self.property_type.short_value
        return "Not Specified"

    @property
    def storage_type_display(self):
        list_of_related_object = self.storage_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def maintenance_fee_type_display(self):
        list_of_related_object = self.maintenance_fee_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def structure_display(self):
        list_of_related_object = self.structure.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def view_type_display(self):
        list_of_related_object = self.view_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def transaction_type_display(self):
        if self.transaction_type:
            return self.transaction_type.short_value
        return "Not Specified"

    @property
    def zoning_type_display(self):
        if self.zoning_type:
            return self.zoning_type.short_value
        return "Not Specified"

    @property
    def ownership_type_display(self):
        if self.ownership_type:
            return self.ownership_type.short_value
        return "Not Specified"

    @property
    def lease_per_time_display(self):
        if self.lease_per_time:
            return self.lease_per_time.short_value
        return ""

    @property
    def core_property_last_updated(self):
        return self.connected_property.last_updated

    def __str__(self, *args, **kwargs):
        return f"{self.connected_property.__str__()}"

    def save(self, *args, **kwargs):

        # Intercepts save to always update the decimal price

        previous_price = self.tracker.previous("price")
        self.previous_price = previous_price

        previous_lease = self.tracker.previous("lease")
        self.previous_lease = previous_lease

        return super().save(*args, **kwargs)


class Building(ConnectedToPropertyBaseModel):

    bathroom_total = models.SmallIntegerField(null=True)
    bedrooms_total = models.SmallIntegerField(null=True)
    bedrooms_above_ground = models.SmallIntegerField(null=True)
    bedrooms_below_ground = models.SmallIntegerField(null=True)
    amenities = models.ManyToManyField(
      PropertyAmenity, related_name="builiding_amenities_set"
    )
    amperage = models.ManyToManyField(
      PropertyAmperage, related_name="building_amperage_set"
    )
    anchor = models.TextField(null=True)
    appliances = models.ManyToManyField(
      PropertyAppliance, related_name="builiding_appliances_set"
    )

    architectural_style = models.ManyToManyField(
      PropertyArchitecturalStyle, related_name="building_architectural_style_set"
    )
    basement_development = models.ManyToManyField(
      PropertyBasementDevelopment, related_name="building_basement_development_set"
    )
    basement_features = models.ManyToManyField(
      PropertyBasementFeature, related_name="building_basement_features_set"
    )
    basement_type = models.ManyToManyField(
      PropertyBasementType, related_name="building_basement_type_set"
    )
    boma_rating = models.TextField(blank=True)

    ceiling_type = models.ManyToManyField(
        PropertyCeilingType, related_name="building_ceiling_type_set"
    )

    ceiling_height = models.DecimalField(
        max_digits=52, decimal_places=2, null=True, blank=True
    )

    ceiling_height_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="building_ceiling_height_set", null=True
    )

    clear_ceiling_height = models.ManyToManyField(
      PropertyClearCeilingHeight, related_name="building_clear_ceiling_height_set"
    )

    constructed_date = models.DateTimeField(
      null=True, blank=True
    )
    construction_material = models.ManyToManyField(
      PropertyConstructionMaterial, related_name="building_construction_material_set"
    )

    construction_status = models.ForeignKey(
      PropertyConstructionStatus, on_delete=models.PROTECT, related_name="building_construction_status_set", null=True
    )
    construction_style_attchment = models.ForeignKey(
      PropertyConstructionStyleAttachment, on_delete=models.PROTECT, related_name="building_construction_style_attchment_set", null=True
    )
    construction_style_other = models.ForeignKey(
      PropertyConstructionStyleOther, on_delete=models.PROTECT, related_name="building_construction_style_other_set", null=True
    )
    construction_style_split_level = models.ForeignKey(
      PropertyConstructionStyleSplitLevel, on_delete=models.PROTECT, related_name="building_construction_style_split_level_set", null=True
    )
    cooling_type = models.ManyToManyField(
      PropertyCoolingType, related_name="building_cooling_type_set"
    )
    energuide_rating = models.TextField(blank=True)
    exterior_finish = models.ManyToManyField(
      PropertyExteriorFinish, related_name="building_exterior_finish_set"
    )
    fireplace_fuel = models.ManyToManyField(
      PropertyFireplaceFuel, related_name="building_fireplace_fuel_set"
    )
    fireplace_present = models.TextField(blank=True)
    fireplace_total = models.IntegerField(null=True, blank=True)
    fireplace_type = models.ManyToManyField(
      PropertyFireplaceType, related_name="building_fireplace_type_set"
    )
    fire_protection = models.ManyToManyField(
      PropertyFireProtection, related_name="building_fire_protection_set"
    )
    fixture = models.ManyToManyField(
      PropertyFixture, related_name="building_fixture_set"
    )
    flooring_type = models.ManyToManyField(
      PropertyFlooringType, related_name="building_flooring_type_set"
    )
    foundation_type = models.ManyToManyField(
      PropertyFoundationType, related_name="building_foundation_type_set",
    )
    half_bath_total = models.IntegerField(null=True, blank=True)
    heating_fuel = models.ManyToManyField(
      PropertyHeatingFuel, related_name="building_heating_fuel_set"
    )
    heating_type = models.ManyToManyField(
      PropertyHeatingType, related_name="building_heating_type_set"
    )

    leeds_category = models.TextField(blank=True)
    leeds_rating = models.TextField(blank=True)

    roof_material = models.ManyToManyField(
      PropertyRoofMaterial, related_name="building_roof_material_set"
    )

    roof_style = models.ManyToManyField(
      PropertyRoofStyle, related_name="building_roof_style_set"
    )

    size_exterior = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    size_exterior_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="building_size_exterior_set", null=True
    )

    size_interior = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    size_interior_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="building_size_interior_set", null=True
    )

    size_interior_finished = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    size_interior_finished_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="building_size_interior_finished_set", null=True
    )

    store_front = models.ManyToManyField(
      PropertyStoreFront, related_name="building_store_front_set"
    )

    # Strange field, crea describes this as number but we get 1.5000
    stories_total = models.TextField(blank=True, null=True)


    total_finished_area = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    total_finished_area_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, related_name="building_total_finished_area_unit_set", null=True
    )

    # This is a building type
    # A special mapping is used here, to not shadow python type keyword while keeping
    # our sanity on maintaining the third party that was integrated on the system
    model_type = models.ManyToManyField(
      PropertyBuildingType, related_name="building_type_set"
    )
    uffi = models.TextField(blank=True)
    utility_power = models.ManyToManyField(
      PropertyUtilityPower, related_name="building_utility_power_set"
    )

    utility_water = models.ManyToManyField(
      PropertyUtilityWater, related_name="building_utility_water_set"
    )

    connected_property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="Building"
    )

    # vacancy_rate = models.TextField()

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.

    BathroomTotal = models.SmallIntegerField(null=True)
    BedroomsTotal = models.SmallIntegerField(null=True)
    BedroomsAboveGround = models.SmallIntegerField(null=True)
    BedroomsBelowGround = models.SmallIntegerField(null=True)
    Amenities = models.TextField(blank=True)
    Amperage = models.TextField(blank=True)
    Anchor = models.TextField(blank=True)
    Appliances = models.TextField(blank=True)
    ArchitecturalStyle = models.TextField(blank=True)
    BasementDevelopment = models.TextField(blank=True)
    BasementFeatures = models.TextField(blank=True)
    BasementType = models.TextField(blank=True)
    BomaRating = models.TextField(blank=True)
    CeilingHeight = models.TextField(blank=True)
    CeilingType = models.TextField(blank=True)
    ClearCeilingHeight = models.TextField(blank=True)
    ConstructedDate = models.TextField(blank=True)
    ConstructionMaterial = models.TextField(blank=True)
    ConstructionStatus = models.TextField(blank=True)
    ConstructionStyleAttachment = models.TextField(blank=True)
    ConstructionStyleOther = models.TextField(blank=True)
    ConstructionStyleSplitLevel = models.TextField(blank=True)
    CoolingType = models.TextField(blank=True)
    EnerguideRating = models.TextField(blank=True)
    ExteriorFinish = models.TextField(blank=True)
    FireplaceFuel = models.TextField(blank=True)
    FireplacePresent = models.TextField(blank=True)
    FireplaceTotal = models.TextField(blank=True)
    FireplaceType = models.TextField(blank=True)
    FireProtection = models.TextField(blank=True)
    Fixture = models.TextField(blank=True)
    FlooringType = models.TextField(blank=True)
    FoundationType = models.TextField(blank=True)
    HalfBathTotal = models.TextField(blank=True)
    HeatingFuel = models.TextField(blank=True)
    HeatingType = models.TextField(blank=True)
    LeedsCategory = models.TextField(blank=True)
    LeedsRating = models.TextField(blank=True)
    RoofMaterial = models.TextField(blank=True)
    RoofStyle = models.TextField(blank=True)
    SizeExterior = models.TextField(blank=True)
    SizeInterior = models.TextField(blank=True)
    StoreFront = models.TextField(blank=True)
    StoriesTotal = models.TextField(blank=True)
    TotalFinishedArea = models.TextField(blank=True)
    Type = models.TextField(blank=True)
    Uffi = models.TextField(blank=True)
    UtilityPower = models.TextField(blank=True)
    UtilityWater = models.TextField(blank=True)
    VacancyRate = models.TextField(blank=True)

    @property
    def size_interior_display(self):
        value = None
        if self.size_interior:
            return f"{int(self.size_interior)} {self.size_interior_unit.display_unit}"
        return value

    @property
    def architectural_style_display(self):
      list_of_related_object = self.architectural_style.all().values_list("short_value", flat=True)
      return ', '.join(list_of_related_object)


    @property
    def model_type_display(self):
        list_of_related_object = self.model_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def appliances_display(self):
        list_of_related_object = self.appliances.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def basement_features_display(self):
        list_of_related_object = self.basement_features.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def basement_type_display(self):
        list_of_related_object = self.basement_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def constructed_date_display(self):
        if self.constructed_date:
            return self.constructed_date.year
        return None

    @property
    def exterior_finish_display(self):
        list_of_related_object = self.exterior_finish.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def flooring_type_display(self):
        list_of_related_object = self.flooring_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def foundation_type_display(self):
        list_of_related_object = self.foundation_type.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def roof_material_display(self):
        list_of_related_object = self.roof_material.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def roof_style_display(self):
        list_of_related_object = self.roof_style.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def utility_water_display(self):
        list_of_related_object = self.utility_wate.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    def __str__(self, *args, **kwargs):
        return f"{self.connected_property.__str__()}"


class AlternateURL(ConnectedToPropertyBaseModel):

    brochure_link = models.CharField(max_length=255, blank=True)
    map_link = models.CharField(max_length=255, blank=True)
    photo_link = models.CharField(max_length=255, blank=True)
    sound_link = models.CharField(max_length=255, blank=True)
    video_link = models.CharField(max_length=255, blank=True)
    connected_property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="alternate_url"
    )

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW
    BrochureLink = models.TextField(blank=True)
    MapLink = models.TextField(blank=True)
    PhotoLink = models.TextField(blank=True)
    SoundLink = models.TextField(blank=True)
    VideoLink = models.TextField(blank=True)


    def __str__(self, *args, **kwargs):
        return f"{self.connected_property.__str__()}"


class Business(ConnectedToPropertyBaseModel):

    business_type = models.ManyToManyField(
      PropertyBusinessType, related_name="business_type_set"
    )
    business_sub_type = models.ManyToManyField(
      PropertyBusinessSubType, related_name="business_sub_type_set"
    )
    established_late = models.DateTimeField(blank=True, null=True)
    franchise = models.BooleanField(blank=True, null=True)
    name = models.TextField(blank=True)
    operating_since = models.DateTimeField(blank=True, null=True)

    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="business_set"
    )

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    BusinessType = models.TextField(blank=True)
    BusinessSubType = models.TextField(blank=True)
    EstablishedDate = models.TextField(blank=True)
    Franchise = models.TextField(blank=True)
    Name = models.TextField(blank=True)
    OperatingSince = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Businesses"

    def __str__(self, *args, **kwargs):
        return f"{self.BusinessType} ({self.connected_property.__str__()})"


class Event(ConnectedToPropertyBaseModel):

    # NOTE: Fields are still camel case due to how parser inserts the field.
    # We need to change these when we overhaul the ddf manager

    Event = models.TextField(blank=True)
    StartDateTime = models.TextField(blank=True)
    EndDateTime = models.TextField(blank=True)
    Comments = models.TextField(blank=True)
    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="events"
    )

    def __str__(self, *args, **kwargs):
        event = "Untitled Event"
        if self.Event:
            event = self.Event
        return f"{self.connected_property.__str__()} ({event})"


class AgentDetails(ConnectedToPropertyBaseModel):

    # NOTE: Fields are still camel case due to how parser inserts the field.
    # We need to change these when we overhaul the ddf manager

    ddf_id = models.TextField(blank=True, null=True, default=None)
    name = models.CharField(max_length=225, blank=True)
    position = models.CharField(max_length=225, blank=True)
    last_updated = models.DateTimeField(
        blank=True, null=True
    )
    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, null=True, related_name="Agent"
    )

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    DDF_ID = models.TextField(blank=True, null=True, default=None)
    Name = models.TextField(blank=True)
    LastUpdated = models.TextField(blank=True)
    Position = models.TextField(blank=True)


    class Meta:
        verbose_name_plural = "Agent Details"

    def __str__(self, *args, **kwargs):
        return f"{self.Name}"


class OfficeDetails(AgentConnectedBaseModel):

    ddf_id = models.TextField(blank=True, null=True, default=None)
    name = models.CharField(max_length=225, null=True)
    last_updated = models.DateTimeField(
        blank=True, null=True
    )
    logo_last_updated = models.DateTimeField(
        blank=True, null=True
    )
    logo_url = models.CharField(max_length=225, null=True)

    organization_type = models.ForeignKey(
        OfficeOrganizationType, on_delete=models.PROTECT, null=True, related_name="office_organization_type_set"
    )

    organization_designation = models.ForeignKey(
        OfficeOrganizationDesignation, on_delete=models.PROTECT, null=True, related_name="office_organization_designation_set"
    )

    organization_franchisor = models.ForeignKey(
        OfficeFranchisor, on_delete=models.PROTECT, null=True, related_name="office_organization_franchisor_set"
    )

    agent = models.OneToOneField(
        AgentDetails, on_delete=models.CASCADE, null=True, related_name="Office"
    )

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW
    DDF_ID = models.TextField(blank=True, null=True, default=None)
    Name = models.TextField(blank=True)
    LastUpdated = models.TextField(blank=True)
    LogoLastUpdated = models.TextField(blank=True)
    OrganizationType = models.TextField(blank=True)
    Designation = models.TextField(blank=True)
    Franchisor = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Office Details"

    def __str__(self, *args, **kwargs):
        return f"{self.name}"


class Address(ConnectedToPropertyBaseModel):


    street_address = models.TextField(blank=True)
    address_line1 = models.TextField(blank=True)
    address_line2 = models.TextField(blank=True)
    street_number = models.TextField(blank=True)
    street_direction_prefix = models.TextField(blank=True)
    street_name = models.TextField(blank=True)
    street_suffix = models.TextField(blank=True)
    street_direction_suffix = models.TextField(blank=True)
    unit_number = models.TextField(blank=True)
    box_number = models.TextField(blank=True)
    city = models.TextField(blank=True)
    province = models.TextField(blank=True)
    postal_code = models.TextField(blank=True)
    country = models.TextField(blank=True)
    additional_street_info = models.TextField(blank=True)
    community_name = models.TextField(blank=True)
    neighbourhood = models.TextField(blank=True)
    subdivision = models.TextField(blank=True)

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    StreetAddress = models.TextField(blank=True)
    AddressLine1 = models.TextField(blank=True)
    AddressLine2 = models.TextField(blank=True)
    StreetNumber = models.TextField(blank=True)
    StreetDirectionPrefix = models.TextField(blank=True)
    StreetName = models.TextField(blank=True)
    StreetSuffix = models.TextField(blank=True)
    StreetDirectionSuffix = models.TextField(blank=True)
    UnitNumber = models.TextField(blank=True)
    BoxNumber = models.TextField(blank=True)
    City = models.TextField(blank=True)
    Province = models.TextField(blank=True)
    PostalCode = models.TextField(blank=True)
    Country = models.TextField(blank=True)
    AdditionalStreetInfo = models.TextField(blank=True)
    CommunityName = models.TextField(blank=True)
    Neighbourhood = models.TextField(blank=True)
    Subdivision = models.TextField(blank=True)

    agent = models.OneToOneField(
        AgentDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="Address",
    )
    connected_property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="Address",
    )
    office = models.OneToOneField(
        OfficeDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="Address",
    )

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self, *args, **kwargs):
      if self.AddressLine1 == "":
        return f"{self.street_address}, {self.city}"
      else:
        return f"{self.address_line1}, {self.city}"


class Phone(AgentConnectedBaseModel):
    text = models.TextField(blank=True)
    contact_type = models.CharField(max_length=225, blank=True)
    phone_type = models.CharField(max_length=225, blank=True)

    agent = models.ForeignKey(
        AgentDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="agent_phone",
    )

    agent = models.ForeignKey(
        AgentDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="Phone",
    )
    office = models.ForeignKey(
        OfficeDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="Phone",
    )

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    ContactType = models.TextField(blank=True)
    PhoneType = models.TextField(blank=True)

    def __str__(self, *args, **kwargs):
        return f"{self.text} ({self.phone_type})"


class Website(AgentConnectedBaseModel):

    contact_type = models.CharField(max_length=225, blank=True)
    wesbite_type = models.CharField(max_length=225, blank=True)
    text = models.TextField(blank=True)
    agent = models.ForeignKey(
        AgentDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="website",
    )
    office = models.ForeignKey(
        OfficeDetails,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="website",
    )
    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW
    ContactType = models.TextField(blank=True)
    WebsiteType = models.TextField(blank=True)

    def __str__(self, *args, **kwargs):
        return f"{self.text}"


class PropertyPhoto(ConnectedToPropertyBaseModel):

    sequence_id = models.SmallIntegerField(blank=True, default=0)
    last_updated = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True)

    # Saved src url, right here. These are currently used for email part
    # as to lessen the spam points given by the email provider.
    # (Embedded photos are discouraged by most email providers)
    # These can also be used once, our client decides to stop saving the photos.
    large_photo_url = models.URLField(blank=True)
    photo_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)


    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="Photos"
    )


    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW
    SequenceId = models.SmallIntegerField(null=True)
    LastUpdated = models.TextField(blank=True)
    Description = models.TextField(blank=True)
    LargePhotoURL = models.URLField(blank=True)
    PhotoURL = models.URLField(blank=True)
    ThumbnailURL = models.URLField(blank=True)

    def __str__(self, *args, **kwargs):
        return f"{self.connected_property.__str__()}'s number {self.sequence_id} picture "

    @property
    def media_url(self, *args, **kwargs):

        # AWS Setting
        # return f"{settings.LISTING_DIR}/{self.Property.DDF_ID}/{self.SequenceId}.jpg"

        # We should let pillow handle this and update the ddf manager if we have time!
        if self.connected_property.listing_type == 2:
          #incase we have to change the bucket so that old data with old bucket address will still be able to display images
          return f"{settings.AWS_MEDIA_ROOT_URL}/{self.large_photo_url}"
        return self.large_photo_url

    class Meta:
        ordering = [
            "sequence_id",
        ]


class Land(ConnectedToPropertyBaseModel):

    size_total = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    size_total_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_size_total_set"
    )

    size_total_text = models.TextField(blank=True)

    size_frontage = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )
    size_frontage_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_size_frontage_set"
    )
    access_type = models.ManyToManyField(
      PropertyAccessType, related_name="land_access_type_set"
    )
    acreage = models.BooleanField(blank=True, null=True)
    amenities = models.ManyToManyField(
      PropertyAmenityNearby, related_name="land_amenities_set"
    )

    cleared_total = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    cleared_total_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_cleared_total_set"
    )
    current_use = models.ManyToManyField(
      PropertyCurrentUse, related_name="land_current_use_set"
    )
    divisble = models.BooleanField(
      blank=True, null=True
    )

    fence_total = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    fence_total_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_fence_total_set"
    )

    fence_type = models.ManyToManyField(
        PropertyFenceType, related_name="land_fence_type_set"
    )

    fronts_on = models.ForeignKey(
        PropertyFrontsOn, on_delete=models.PROTECT, null=True, related_name="land_fronts_on_set"
    )

    land_disposition = models.ManyToManyField(
        PropertyLandDispositionType, related_name="land_disposition_set"
    )

    landscape_features = models.ManyToManyField(
      PropertyLandscapeFeature, related_name="land_landscape_features_set"
    )

    pasture_total = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    pasture_total_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_pasture_total_set"
    )

    sewer = models.ManyToManyField(
      PropertySewer, related_name="land_sewer_set"
    )

    size_depth = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    size_depth_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_size_depth_set"
    )

    soil_evaluation = models.ForeignKey(
      PropertySoilEvaluationType, on_delete=models.PROTECT, null=True,  related_name="land_soil_evaluation_set"
    )

    soil_type = models.ManyToManyField(
      PropertySoilType
    )

    surface_water = models.ManyToManyField(
      PropertySurfaceWater
    )

    tiled_total = models.DecimalField(
        max_digits=50, decimal_places=2, null=True, blank=True
    )

    tiled_total_unit = models.ForeignKey(
      PropertyMeasureUnit, on_delete=models.PROTECT, null=True, related_name="land_tiled_total_set"
    )

    connected_property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="land"
    )


    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    SizeTotal = models.TextField(blank=True)
    SizeTotalText = models.TextField(blank=True)
    SizeFrontage = models.TextField(blank=True)
    AccessType = models.TextField(blank=True)
    Amenities = models.TextField(blank=True)
    ClearedTotal = models.TextField(blank=True)
    CurrentUse = models.TextField(blank=True)
    Divisible = models.TextField(blank=True)
    FenceTotal = models.TextField(blank=True)
    FenceType = models.TextField(blank=True)
    FrontsOn = models.TextField(blank=True)
    LandDisposition = models.TextField(blank=True)
    LandscapeFeatures = models.TextField(blank=True)
    PastureTotal = models.TextField(blank=True)
    Sewer = models.TextField(blank=True)
    SizeDepth = models.TextField(blank=True)
    SoilEvaluation = models.TextField(blank=True)
    SoilType = models.TextField(blank=True)
    SurfaceWater = models.TextField(blank=True)
    TiledTotal = models.TextField(blank=True)

    def __str__(self, *args, **kwargs):
        return f"{self.connected_property.__str__()}'s Land"

    @property
    def size_total_display(self):
        value = None
        if self.size_total:
            return f"{int(self.size_total)} {self.size_total_unit.display_unit}"
        return value

    @property
    def fence_type_display(self):
        if self.fence_type:
            return self.fence_type.short_value
        return None

    @property
    def landscape_features_display(self):
        list_of_related_object = self.landscape_features.active_objects.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)

    @property
    def sewer_display(self):
        list_of_related_object = self.sewer.active_objects.all().values_list("short_value", flat=True)
        return ', '.join(list_of_related_object)


class Parking(ConnectedToPropertyBaseModel):

    name = models.ForeignKey(
      PropertyParkingType, on_delete=models.PROTECT, null=True
    )
    spaces = models.CharField(max_length=225, blank=True)

    # These are the owner ship type and their id constants defined on crea data
    ATTACHED_GARAGE = 1
    INTEGRATED_GARAGE = 2
    DETACHED_GARAGE = 3
    GARAGE = 4
    CARPORT = 5
    UNDERGROUND = 6
    INDOOR = 7
    OPEN = 8
    COVERED = 9
    PARKING_PAD = 10
    PAVED_YARD = 11
    OTHER = 12
    NONE = 13
    UNKNOWN = 14
    NO_GARAGE = 15
    PARKING_SPACE_CATEGORY = 16
    PARKADE = 17
    STALL = 18
    BREEZEWAY = 19
    OFFSET = 20
    REAR = 21
    RV = 22
    STREET = 23
    OVERSIZE = 24
    SEE_REMARKS = 25
    INSIDE_ENTRY = 26
    GRAVEL = 27
    INTERLOCKED = 28
    SHARED = 29
    STREET_PERMIT = 30
    SURFACED = 31
    TANDEM = 32
    EXPOSED_AGGREGATE = 33
    VISITOR_PARKING = 34
    BOAT_HOUSE = 35
    CONCRETE = 36
    HEATED_GARAGE = 37
    ELECTRIC_VEHICLE_CHARGING_PARKING = 38

    PARKING_TYPE = (
        (ATTACHED_GARAGE, "Attached garage"),
        (INTEGRATED_GARAGE, "Integrated garage"),
        (DETACHED_GARAGE, "Detached garage"),
        (GARAGE, "Garage"),
        (CARPORT, "Carport"),
        (UNDERGROUND, "Underground"),
        (INDOOR, "Indoor"),
        (OPEN, "Open"),
        (COVERED, "Covered"),
        (PARKING_PAD, "Parking pad"),
        (PAVED_YARD, "Paved Yard"),
        (OTHER, "Other"),
        (NONE, "None"),
        (UNKNOWN, "Unknown"),
        (NO_GARAGE, "No Garage"),
        (PARKING_SPACE_CATEGORY, "Parking Space(s)"),
        (PARKADE, "Parkade"),
        (STALL, "Stall"),
        (BREEZEWAY, "Breezeway"),
        (OFFSET, "Offset"),
        (REAR, "Rear"),
        (RV, "RV"),
        (STREET, "Street"),
        (OVERSIZE, "Oversize"),
        (SEE_REMARKS, "See Remarks"),
        (INSIDE_ENTRY, "Inside Entry"),
        (GRAVEL, "Gravel"),
        (INTERLOCKED, "Interlocked"),
        (SHARED, "Shared"),
        (STREET_PERMIT, "Street Permit"),
        (SURFACED, "Surfaced"),
        (TANDEM, "Tandem"),
        (EXPOSED_AGGREGATE, "Exposed Aggregate"),
        (VISITOR_PARKING, "Visitor parking"),
        (BOAT_HOUSE, "Boat House"),
        (CONCRETE, "Concrete"),
        (HEATED_GARAGE, "Heated Garage"),
        (ELECTRIC_VEHICLE_CHARGING_PARKING, "Electric Vehicle Charging Station(s)"),
    )


    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="Parking"
    )

    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    Name = models.TextField()
    Spaces = models.TextField()

    @classmethod
    def get_praking_type(cls, id):
        return dict(cls.PARKING_TYPE).get(id)

    def __str__(self, *args, **kwargs):
        if self.name:
            return self.name.short_value
        return None

    @property
    def name_display(self):
        if self.name:
            return self.name.short_value
        return None


class Utility(ConnectedToPropertyBaseModel):

    # This is the utility type
    # A special mapping is used here, to not shadow python type keyword while keeping
    # our sanity on maintaining the third party that was integrated on the system
    model_type = models.ForeignKey(
        PropertyUtilityType, on_delete=models.PROTECT, null=True
    )

    # Description returns a lookup but not one documentation mentions this lookup...
    description = models.TextField()

    connected_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="utility"
    )


    # TODO: Fields and choices below are how the old parser works
    # create a new custom migration to try and port these fields to the new one
    # and remove choices that we don't use anymore.
    # NOTE: DO NOT USE CHOICES BELOW

    Type = models.TextField(blank=True)
    Description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Utilities"

    def __str__(self, *args, **kwargs):
        return f"{self.model_type}"


class Failed_Photos_Redownloads(CommonInfo):

    # NOTE: Fields are still camel case due to how parser inserts the field.
    # We need to change these when we overhaul the ddf manager

    DDF_ID = models.TextField(blank=True)
    Photo_ID = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Failed Photos Redownloads"

    def __str__(self, *args, **kwargs):
        return f"{self.Photo_ID} - {self.DDF_ID}"


class Geolocation(ConnectedToPropertyBaseModel):
    coordinates = geomodels.PointField(blank=True, null=True)
    connected_property = models.OneToOneField(
        Property, on_delete=models.CASCADE, related_name="Geo"
    )

    def __str__(self, *args, **kwargs):
        if self.coordinates:
            return f"{self.coordinates.x}, {self.coordinates.y}"
        else:
            return "No coordinates"

    @property
    def base_address(self):
        address = self.connected_property.Address
        return f"{address.street_address} {address.city} {address.province} {address.postal_code}"

    @property
    def lng(self):
        if self.coordinates.x:
            return f"{self.coordinates.x}"
        else:
            return "No latitude"

    @property
    def lat(self):
        if self.coordinates.y:
            return f"{self.coordinates.y}"
        else:
            return "No longitude"


class DDF_LastUpdate(CommonInfo):

    # NOTE: Fields are still camel case due to how parser inserts the field.
    # We need to change these when we overhaul the ddf manager

    LastUpdate = models.TextField(default="2012-08-08T21:54:28Z")
    UpdateType = models.TextField(unique=True, default="DDF")

    def __str__(self, *args, **kwargs):
        return f"{self.LastUpdate}"

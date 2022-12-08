from core.models import CommonInfo
from core.shortcuts import get_object_or_None

from django.contrib.postgres.fields import ArrayField
from django.db import models

from crea_parser.mixins import CreaModelBaseMetaDataManager

# As discovered metadata fields are added from time to time. we need to catch these changes!


class CreaMetaDataCommonInfo(CommonInfo, CreaModelBaseMetaDataManager):

    class Meta:
        abstract = True

    crea_metadata_manager = CreaModelBaseMetaDataManager()

    # yes, sadly metadata id on crea contains strings...
    metadata_entry_id = models.CharField(max_length=255)

    # This might be a little bit off on the data type, but I can't find the data type on the docs
    # so let's go with string here for flexibility
    value = models.CharField(max_length=225, blank=True, null=True)
    long_value = models.CharField(max_length=1024, blank=True, null=True)
    short_value = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return f"{self.metadata_entry_id} - {self.long_value}"


class PropertyAccessType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "AccessType"


class PropertyAmenity(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Amenities"


class PropertyAmenityNearby(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "AmenitiesNearby"


class PropertyAmperage(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Amperage"


class PropertyAppliance(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Appliances"


class PropertyArchitecturalStyle(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ArchitecturalStyle"


class PropertyBasementDevelopment(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "BasementDevelopment"


class PropertyBasementFeature(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "BasementFeatures"


class PropertyBasementType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "BasementType"


class PropertyBoard(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Boards"


class PropertyBuildingType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "BuildingType"


class PropertyBusinessSubType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "BusinessSubType"


class PropertyBusinessType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "BusinessType"


class PropertyCeilingType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "CeilingType"


class PropertyClearCeilingHeight(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ClearCeilingHeight"


class PropertyCommunicationType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "CommunicationType"


class PropertyCommunityFeature(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "CommunityFeatures"


class PropertyConstructionMaterial(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ConstructionMaterial"


class PropertyConstructionStatus(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ConstructionStatus"


class PropertyConstructionStyleAttachment(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ConstructionStyleAttachment"


class PropertyConstructionStyleOther(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ConstructionStyleOther"


class PropertyConstructionStyleSplitLevel(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ConstructionStyleSplitLevel"


class PropertyCoolingType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "CoolingType"


class PropertyCrop(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Crop"


class PropertyCurrentUse(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "CurrentUse"


class PropertyDocumentType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "DocumentType"


class PropertyEasement(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Easement"


class PropertyEquipmentType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "EquipmentType"


class PropertyExteriorFinish(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ExteriorFinish"


class PropertyFarmType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FarmType"


class PropertyFeature(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Features"


class PropertyFenceType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FenceType"


class PropertyFireProtection(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FireProtection"


class PropertyFireplaceFuel(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FireplaceFuel"


class PropertyFireplaceType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FireplaceType"


class PropertyFixture(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Fixture"


class PropertyFlooringType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FlooringType"


class PropertyFoundationType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FoundationType"


class PropertyFrontsOn(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "FrontsOn"


class PropertyHeatingType(CreaMetaDataCommonInfo):
    resource = "Property"
    # So yes, there's a space on crea...
    lookup_name = "Heating Type"


class PropertyHeatingFuel(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "HeatingFuel"


class PropertyIrrigationType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "IrrigationType"


class PropertyLandDispositionType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "LandDispositionType"


class PropertyLandscapeFeature(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "LandscapeFeatures"


class PropertyLeaseType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "LeaseType"


class PropertyLiveStockType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "LiveStockType"


class PropertyLoadingType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "LoadingType"


class PropertyMachinery(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Machinery"


class PropertyMaintenanceFeeType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "MaintenanceFeeType"


class PropertyMeasureUnit(CreaMetaDataCommonInfo):

    homeswipr_short_value = models.CharField(max_length=15)

    # TODO: Everytime we fetch from the crea metadata
    # there's no meta data entry with 3 and 1 BUT 
    # We are getting unit with an id of 3 and 1 from the
    # properties itself...
    # We need to check these two metadata entry id and where they 
    # come from
    resource = "Property"
    lookup_name = "MeasureUnit"

    @property
    def display_unit(self):
        if self.homeswipr_short_value:
            return self.homeswipr_short_value
        return self.short_value


class PropertyOwnershipType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "OwnershipType"


class PropertyParkingType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ParkingType"


class PropertyPaymentUnit(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "PaymentUnit"


class PropertyPoolFeature(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "PoolFeatures"


class PropertyPoolType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "PoolType"


class PropertyPropertyType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "PropertyType"

    # This is a very important metadata entry for homeswipr
    # so we decided to put this as a constant here
    SINGLE_FAMILY_METADATA_ENTRY_ID = 300

    # A boolean if we want to filter with our normal search
    include_on_base_homeswipr_filter = models.BooleanField(default=True)

    @classmethod
    def get_valid_property_type_as_list(cls):
        # Gets all the base filter we need as list integer
        return cls.active_objects.filter(
            include_on_base_homeswipr_filter=True
        ).values_list('pk', flat=True)


class PropertyRentalEquipmentType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RentalEquipmentType"


class PropertyRightType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RightType"


class PropertyRoadType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RoadType"


class PropertyRoofMaterial(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RoofMaterial"


class PropertyRoofStyle(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RoofStyle"


class PropertyRoomLevel(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RoomLevel"


class PropertyRoomType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "RoomType"


class PropertySewer(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "Sewer"


class PropertySignType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "SignType"


class PropertySoilEvaluationType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "SoilEvaluationType"


class PropertySoilType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "SoilType"


class PropertyStorageType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "StorageType"


class PropertyStoreFront(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "StoreFront"


class PropertyStructureType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "StructureType"


class PropertySurfaceWater(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "SurfaceWater"


class PropertyTopographyType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "TopographyType"


class PropertyTransactionType(CreaMetaDataCommonInfo):

    # Some transaction type are (For rent or for sale)
    # which we need cater the other for rent and for sale
    included_on_filter_transaction_type_metadata_id = ArrayField(
        models.IntegerField(), null=True, blank=True
    )

    resource = "Property"
    lookup_name = "TransactionType"

        
    @classmethod
    def get_true_values_for_transaction_type(cls, metadata_entry_id):

        list_of_included_metadata_entry = get_object_or_None(
            cls.active_objects,
            metadata_entry_id=metadata_entry_id
        ).included_on_filter_transaction_type_metadata_id

        if list_of_included_metadata_entry:
            list_of_included_metadata_entry.append(metadata_entry_id)
            return list_of_included_metadata_entry

        return [metadata_entry_id]

class PropertyUffiCode(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "UffiCodes"


class PropertyUtilityPower(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "UtilityPower"


class PropertyUtilityType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "UtilityType"


class PropertyUtilityWater(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "UtilityWater"


class PropertyViewType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ViewType"


class PropertyWaterFrontType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "WaterFrontType"


class PropertyZoningType(CreaMetaDataCommonInfo):
    resource = "Property"
    lookup_name = "ZoningType"


class AgentBoard(CreaMetaDataCommonInfo):
    resource = "Agent"
    lookup_name = "Boards"


class AgentIndividualDesignation(CreaMetaDataCommonInfo):
    resource = "Agent"
    lookup_name = "IndividualDesignations"


class AgentLanguage(CreaMetaDataCommonInfo):
    resource = "Agent"
    lookup_name = "Languages"


class AgentSpecialtie(CreaMetaDataCommonInfo):
    resource = "Agent"
    lookup_name = "Specialties"

class OfficeFranchisor(CreaMetaDataCommonInfo):

    resource = "Office"
    lookup_name = "Franchisor"

class OfficeOrganizationType(CreaMetaDataCommonInfo):

    resource = "Office"
    lookup_name = "OrganizationType"


class OfficeOrganizationDesignation(CreaMetaDataCommonInfo):

    resource = "Office"
    lookup_name = "OrganizationDesignations"

# Also find a better way to implement this!
metadata_models = [PropertyAccessType, PropertyAmenity, PropertyAmenityNearby, PropertyAmperage, 
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
]

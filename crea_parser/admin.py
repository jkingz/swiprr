from django.contrib import admin
from django.contrib.gis import admin as geo_admin

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
from .models import (
    Address,
    AgentDetails,
    AlternateURL,
    Building,
    Business,
    DDF_LastUpdate,
    Event,
    Failed_Photos_Redownloads,
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
    Website
)


class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "property_listing_id",
        "property_ddf_id",
        "creation_date",
        "last_updated"
    )
    readonly_fields = ("creation_date", "last_updated",)
    search_fields = (
        "listing_id",
        "ddf_id",
        "pk",
    )
    list_filter = ("is_active",)


class RoomAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    list_display = ("__str__", "property_listing_id", "property_ddf_id",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_filter = ("is_active",)


class PropertyInfoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "property_listing_id", "property_ddf_id", "price", "transaction_type")
    autocomplete_fields = ("connected_property",)
    readonly_fields = ("listing_contract_date", "price")
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_filter = ("is_active",)


class BuildingAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_filter = ("is_active",)


class AlternateURLAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "video_link", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class BusinessAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class EventAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class AgentDetailsAdmin(admin.ModelAdmin):
    search_fields = ("Name",)
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id", "ddf_id")
    list_filter = ("is_active",)


class AddressAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        "connected_property",
        "agent",
        "office",
    )
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class PropertyPhotoAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
        "connected_property__id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class LandAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class ParkingAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "connected_property", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class UtilityAdmin(admin.ModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class FailedPhotosRedownloadsAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    list_filter = ("is_active",)


class GeolocationAdmin(geo_admin.GeoModelAdmin):
    autocomplete_fields = ("connected_property",)
    search_fields = (
        "connected_property__listing_id",
        "connected_property__ddf_id",
    )
    list_display = ("__str__", "base_address", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class OfficeDetailsdmin(admin.ModelAdmin):
    search_fields = ("Name",)
    autocomplete_fields = ("agent",)
    list_display = ("__str__", "agent", "property_listing_id", "property_ddf_id")
    list_filter = ("is_active",)


class PhoneAdmin(admin.ModelAdmin):
    autocomplete_fields = ("agent", "office")
    list_display = (
        "__str__",
        "agent",
        "office",
        "contact_type",
        "property_listing_id",
        "property_ddf_id",
    )
    list_filter = ("is_active",)


class WebsiteAdmin(admin.ModelAdmin):
    autocomplete_fields = ("agent", "office")
    list_display = (
        "__str__",
        "agent",
        "office",
        "property_listing_id",
        "property_ddf_id",
    )
    list_filter = ("is_active",)


class DDFLastUpdateAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    list_filter = ("is_active",)


class PropertyClearCeilingHeightAdmin(admin.ModelAdmin):
    pass


class PropertyPropertyTypeAdmin(admin.ModelAdmin):
    pass


class PropertyTransactionTypeAdmin(admin.ModelAdmin):
    pass

class PropertyMeasureUnitAdmin(admin.ModelAdmin):
    pass


class PropertyBuildingTypeAdmin(admin.ModelAdmin):
    pass


class PropertyBasementTypeAdmin(admin.ModelAdmin):
    pass


class PropertyBasementFeatureAdmin(admin.ModelAdmin):
    pass


class PropertyArchitecturalStyleAdmin(admin.ModelAdmin):
    pass


admin.site.register(PropertyArchitecturalStyle, PropertyArchitecturalStyleAdmin)
admin.site.register(PropertyMeasureUnit, PropertyMeasureUnitAdmin)
admin.site.register(PropertyTransactionType, PropertyTransactionTypeAdmin)
admin.site.register(PropertyPropertyType, PropertyPropertyTypeAdmin)
admin.site.register(PropertyClearCeilingHeight, PropertyClearCeilingHeightAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(AlternateURL, AlternateURLAdmin)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(PropertyInfo, PropertyInfoAdmin)
admin.site.register(AgentDetails, AgentDetailsAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PropertyPhoto, PropertyPhotoAdmin)
admin.site.register(Land, LandAdmin)
admin.site.register(Parking, ParkingAdmin)
admin.site.register(Utility, UtilityAdmin)
admin.site.register(Failed_Photos_Redownloads, FailedPhotosRedownloadsAdmin)
admin.site.register(Geolocation, GeolocationAdmin)
admin.site.register(OfficeDetails, OfficeDetailsdmin)
admin.site.register(Phone, PhoneAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(DDF_LastUpdate, DDFLastUpdateAdmin)
admin.site.register(PropertyBuildingType, PropertyBuildingTypeAdmin)
admin.site.register(PropertyBasementType, PropertyBasementTypeAdmin)
admin.site.register(PropertyBasementFeature, PropertyBasementFeatureAdmin)

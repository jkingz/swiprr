import decimal
import parser

from crea_parser.models import *
from crea_parser.submodels.metadata import metadata_models
from .ddf_logger import logger

###This file is used to map the values retrived from the ddf_client to the Django database.
### Each list contains a tuple or more representing the following:
###(Table Name in DDF, Table Object in DB, Table fields key in db_fields, children dictionary as per DDF Standard)


building_children = [
    ("Rooms", Room, "room_fields", "Room"),
]

office_children = [
    ("Address", Address, "address_fields", None),
    ("Phones", Phone, "phones_fields", "Phone"),
    ("Websites", Website, "websites_fields", "Website"),
]

agent_children = [
    ("Address", Address, "address_fields", None),
    ("Phones", Phone, "phones_fields", "Phone"),
    ("Websites", Website, "phones_fields", "Website"),
    # ('Specialties', AgentSpecialities, 'agent_specialties_fields', 'Specialty'),
    # ('Designations ', AgentSpecialities, 'agent_designations_fields','Designation'),
    # ('Languages ', AgentLanguages,'agent_languages_fields','Language'),
    # ('TradingAreas ', AgentTradingAreas,'agent_trading_areas_fields','TradingArea'),
]

# defines only simple children that doesn't children
property_children = [
    ("Photo", PropertyPhoto, "property_photo_fields", "PropertyPhoto"),
    ("Address", Address, "address_fields", None),
    ("Land", Land, "land_fields", None),
    ("Business", Business, "business_fields", None),
    ("AlternateURL", AlternateURL, "alternate_url_fields", None),
    ("ParkingSpaces", Parking, "parking_fields", "Parking"),
    ("UtilitiesAvailable", Utility, "utility_fields", "Utility"),
    ("OpenHouse", Event, "event_fields", "Event"),
]
# used to rename fields
rename_fields_dict = {"ID": "ddf_id", "#text": "text", "Type": "model_type", "Property": "connected_property"}

# Map field with their corresponding internal_type
def get_field_and_matching_internal_values(model_meta_fields):
    output = {}
    for field in model_meta_fields:

        related_query_name = ""

        try:
            related_query_name = field.related_query_name()
        except Exception as e:
            # logger.debug(f"Field {field} has no related name")
            related_query_name = None

        output[field.name] = {
            'internal_type': field.get_internal_type(),
            'related_query_name': related_query_name
        }

    return output

# fields names as per the model for each table
# and now with their respective type
db_fields = {
    "property_fields": get_field_and_matching_internal_values(Property._meta.get_fields()),
    "property_info_fields": get_field_and_matching_internal_values(PropertyInfo._meta.get_fields()),
    "building_fields": get_field_and_matching_internal_values(Building._meta.get_fields()),
    "room_fields": get_field_and_matching_internal_values(Room._meta.get_fields()),
    "land_fields": get_field_and_matching_internal_values(Land._meta.get_fields()),
    "address_fields": get_field_and_matching_internal_values(Address._meta.get_fields()),
    "business_fields": get_field_and_matching_internal_values(Business._meta.get_fields()),
    "alternate_url_fields": get_field_and_matching_internal_values(AlternateURL._meta.get_fields()),
    "parking_fields": get_field_and_matching_internal_values(Parking._meta.get_fields()),
    "property_photo_fields": get_field_and_matching_internal_values(PropertyPhoto._meta.get_fields()),
    "utility_fields": get_field_and_matching_internal_values(Utility._meta.get_fields()),
    "event_fields": get_field_and_matching_internal_values(Event._meta.get_fields()),
    "agent_details_fields": get_field_and_matching_internal_values(AgentDetails._meta.get_fields()),
    "office_details_fields": get_field_and_matching_internal_values(OfficeDetails._meta.get_fields()),
    "phones_fields": get_field_and_matching_internal_values(Phone._meta.get_fields()),
    "websites_fields": get_field_and_matching_internal_values(Website._meta.get_fields()),
    #'agent_specialties_fields': [f.name for f in AgentSpecialities._meta.get_fields()],
    #'agent_designations_fields': [f.name for f in AgentDesignations._meta.get_fields()],
    #'agent_languages_fields': [f.name for f in AgentLanguages._meta.get_fields()],
    #'agent_trading_areas_fields': [f.name for f in AgentTradingAreas._meta.get_fields()],
}


class DDFManagerTypeCasting(object):
    """
    A class to handle all different values of ddf manager and
    the expected type on the database field. 
    
    NOTE: Due to a special case from crea (the measure unit with value)
    this returns a dictionary of fields
    """

    model = None
    mode = ""
    field_name = ""
    value = None
    lookup_name = None


    # Field utility passes a lookup object BUT
    # there's no mention of any lookup in the documentation 
    # with that resource name and lookupname
    # so we instead accept it as textfield...
    LOOKUP_TEXT_FIELD_EXCEPTIONS = [
        {"model": "Utility", "field_name": "description"}
    ]

    def __init__(self, model, field_name, value, mode, lookup_name=None):

        self.model = model
        self.mode = mode
        self.value = value
        self.field_name = field_name

        if isinstance(value, dict):

            lookup_name = self.value.get("LookupName", None)
            if lookup_name:
                self.lookup_name = lookup_name

                if self.lookup_name == "HeatingType":
                    # So yes, there's a space on crea when we're trying to
                    # lookup but is passed without space on fetching...
                    # Strange, but can't do anything about it.
                    self.lookup_name = "Heating Type"
            else:
                # The passed dictionary isn't straightforward
                # let's try to get if it has a Unit Key,
                # If it has, this is a PropertyMeasureUnit as stated
                # on the crea docs
                unit = self.value.get("Unit", None)

                if unit:
                    self.lookup_name = "MeasureUnit"
                    self.mode = "MeasureUnitWithValue"

        logger.info(
            f"Class typecasting is instantiated with values of value of '{self.value}', mode of '{self.mode}', and lookup name of '{self.lookup_name}'"
        )

        return super().__init__()

    def type_cast_field(self):
        try:

            raw_value = None

            # Convert fields to something that django can understand and fit
            if self.mode == "MeasureUnitWithValue":
                # A special type caset for a unit with a value
                raw_value = self._type_cast_to_measure_unit_and_value()
            elif self.mode == "CharField" or self.mode == "TextField":
                raw_value = self._type_cast_to_string()
            elif self.mode == "SmallIntegerField" or self.mode == "IntegerField":
                raw_value = self._type_cast_to_integer()
            elif self.mode == "DateTimeField":
                raw_value = self._type_cast_to_date()
            elif self.mode == "BooleanField":
                raw_value = self._type_cast_to_boolean()
            elif self.mode == "DecimalField":
                raw_value = self._type_cast_to_decimal()
            elif self.lookup_name and self.mode == "ForeignKey":
                raw_value = self._type_cast_to_a_single_lookup()
            elif self.lookup_name and self.mode == "ManyToManyField":
                raw_value = self._type_cast_to_a_multiple_lookup()
            elif not self.lookup_name and (self.mode == "ForeignKey" or self.mode == "OneToOneField" or self.mode == "ManyToManyField"):
                # Skip foreign key or one to one field or many to many that has no lookup name
                raw_value = None
            else:
                logger.error(f"Can't get the mode {self.mode} for value of {self.value}, trying to typecast to string")
                raw_value = self._type_cast_to_string()

            # Finalize and return a dictinoary of processed fields..

            # If it's already dictionary, this is already finalized
            # by the function
            if isinstance(raw_value, dict):
                return raw_value
            else:
                return {self.field_name: raw_value}

        except Exception as e:
            logger.error(f"Something went wrong on type casting...")
            logger.error(f"Error message: {e}")
            logger.error(f"Internal values are {self.mode}, {self.value}, {self.lookup_name}")
            return {self.field_name: None}

    def _search_for_metadata_model_lookup(self):

        for model in metadata_models:
            if model.lookup_name == self.lookup_name:
                specific_lookup_model = model
                break
        
        return specific_lookup_model

    def _type_cast_to_measure_unit_and_value(self):
        logger.info(f"Measure unit with value detected, typecasting measure unit with value")

        raw_unit = {"ID": self.value.get("Unit", None)}
        raw_unit_value = self.value.get("#text", None)

        return_value = {}

        if raw_unit_value:
            return_value[self.field_name] = self._type_cast_to_decimal(raw_unit_value)

        if raw_unit:
            return_value[f"{self.field_name}_unit"] = self._type_cast_to_a_single_lookup(self.lookup_name, raw_unit)

        return return_value


    def _type_cast_to_boolean(self):
        if self.value == "true" or self.value == "1" or self.value == 1 or self.value is True:
            return True
        elif self.value == "false" or self.value == "0" or self.value == 0 or self.value is False:
            return False
        return None

    def _type_cast_to_a_multiple_lookup(self):

        # Type cast to a mutiple lookup object
        logger.info(f"Searching for a single lookup for {self.lookup_name} and value of {self.value}")

        specific_lookup_model = None

        specific_lookup_model = self._search_for_metadata_model_lookup()

        if specific_lookup_model:
            queryset_list = list(specific_lookup_model.active_objects.filter(metadata_entry_id__in=self.value.get("ID", "").split(",")))

            if not queryset_list:
                logger.error(f"Lookup with {self.lookup_name} and id of {self.value} not found, Please check the fields")
            else:
                logger.info(f"Multiple lookup found: '{queryset_list}', returning...")
            
            return queryset_list
        else:
            logger.error(f"Can't get the specific lookup model for lookupname {self.lookup_name}")
            return None


    def _type_cast_to_a_single_lookup(self, lookup_name=None,  value=None):
        # Type cast to a lookup object

        if not lookup_name:
            lookup_name = self.lookup_name

        if not value:
            value = self.value

        logger.info(f"Searching for a single lookup for {lookup_name} and value of {value}")

        specific_lookup_model = None
        specific_lookup_model = self._search_for_metadata_model_lookup()

        if specific_lookup_model:
            metadata_row = get_object_or_None(specific_lookup_model.active_objects, metadata_entry_id=value.get('ID'))
            if not metadata_row:
                logger.error(f"Lookup with {lookup_name} and id of {value} not found, Please check the fields")
            else:
                logger.info(f"Lookup found: '{metadata_row}', returning...")
            return metadata_row
        else:
            logger.error(f"Can't get the specific lookup model for lookupname {lookup_name}")
            return None

    def _type_cast_to_integer(self):
        try:
            return int(self.value)
        except Exception as e:
            logger.error(f"Type casting failed on integer with value of {self.value}, returning value as string")
            logger.error(f"Error message is: {e}")
            return str(self.value)

    def _type_cast_to_string(self):
        value = self.value
        for field_exception in self.LOOKUP_TEXT_FIELD_EXCEPTIONS:
            if field_exception.get('model', '') == self.model.__name__ and field_exception.get('field_name') == self.field_name:
                value = self.value.get("#text")
        return str(value)

    def _type_cast_to_date(self):
        try:
            return parser.parse(self.value)
        except TypeError as e:
            logger.info("Type casting failed on datetime, might be already a datetime")
            return self.value
        except ValueError:
            logger.info("Type casting failed on a date failed! ")
            return None

    def _type_cast_to_decimal(self, value=None):

        if not value:
            value = self.value

        if self.value:
            try:
                type_casted_value = decimal.Decimal(value)
                return type_casted_value
            except (decimal.InvalidOperation):
                logger.info("Type casting failed on a decimal failed! ")
                return None
        else:
            # Return None, if value is not passed
            return None

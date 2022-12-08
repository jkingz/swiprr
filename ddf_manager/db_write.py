from core.shortcuts import get_object_or_None, convert_to_snakecase
from dateutil import parser
from django.utils import timezone

from .db_mapping import *
from .db_summary import *

##This file maps the DDF data retrived by the ddf_client to the proper table in the database.

##To understand the structure of the mapping in this files, Please refer to the DDF documenation under:
##https://www.crea.ca/wp-content/uploads/2016/02/Data_Distribution_Facility_Data_Feed_Technical_Documentation.pdf


def handle_filtered_field(TABLE, django_key, input, field_name_and_internal_value, ddf_key):
    # Handle typecast for fields
    logger.info(f"Typecasting the django key of {django_key} and the ddf_key of {ddf_key}")

    type_casted_fields_and_values = DDFManagerTypeCasting(
        TABLE,
        django_key,
        input[ddf_key],
        field_name_and_internal_value[django_key].get("internal_type", "")
    ).type_cast_field()
    return type_casted_fields_and_values

# Adds new attribute to object with a corresponding key
def insert_field_keys_to_output(output_alias, to_insert):
    for key in to_insert.keys():
        output_alias[key] = to_insert[key]

    return output_alias

# filter_fields: used to get fields that are neither a list nor a dictionary elements for saving in db. Also renames the fields if needed.
def filter_fields(TABLE, input, field_name_and_internal_value, rename_fields):
    output = {}
    m2m_output = {}
    if input:
        for key in input.keys():
            snake_case_input_key = convert_to_snakecase(key)
            if not input[key]:
                logger.debug(f"Null value or no key, while getting the key '{key}' in the passed object '{input}'")
                continue
            # rename if in rename_fields
            elif key in rename_fields or snake_case_input_key in field_name_and_internal_value.keys():
                django_key = snake_case_input_key

                if key in rename_fields:
                    django_key = rename_fields[key]

                # Typecast and inserts the typecasted fields to their respective outputs
                if field_name_and_internal_value[django_key].get("internal_type", "") == "ManyToManyField":
                    m2m_output = insert_field_keys_to_output(m2m_output, handle_filtered_field(TABLE, django_key, input, field_name_and_internal_value, key))
                else:
                    output = insert_field_keys_to_output(output, handle_filtered_field(TABLE, django_key, input, field_name_and_internal_value, key))
                
            elif (isinstance(input[key], list)
                or isinstance(input[key], dict)):
                logger.debug(f"Skipping list with dictionary")
                logger.debug(f"A list and dictionary instance with a key of {key} is skipped since it's not part of the field table")
                logger.debug(f"NOTE: this might be a children property")
                logger.debug(f"The object in the input is {input[key]}")
                continue
    return output, m2m_output


def finalize_table_data(TABLE, table_fields, record_obj, record_filtered, m2m_record_filtered, **kwargs):
    # Finalizes table data
    logger.info(f"trying to insert record_filtered with values of {record_filtered} and {kwargs}")

    if record_filtered:
        record_obj = TABLE(**record_filtered, **kwargs)
        record_obj.save()
    
    if m2m_record_filtered:
        for key in m2m_record_filtered.keys():
            m2m_field_manager = getattr(record_obj, key)
            m2m_field_manager.set(m2m_record_filtered[key])

    return record_obj


# update_table: saves a recorded a db table.
# parameters(table in ddf record, Table db Object, db_field, renamed_fields,**kwargs is used to pass parent object by assignment)
def update_table(
    table, TABLE, table_fields, rename_fields=rename_fields_dict, **kwargs
):
    logger.info(f"Processing data into {TABLE}...")

    record_obj = None
    if table:
        if isinstance(table, list):
            for record in table:
                record_filtered, m2m_record_filtered = filter_fields(
                    TABLE, record, table_fields, rename_fields=rename_fields
                )
                logger.info(f"trying to insert record_filtered with values of {record_filtered} and {kwargs}")
                record_obj = finalize_table_data(TABLE, table_fields, record_obj, record_filtered, m2m_record_filtered, **kwargs)

        else:
            record = table
            record_filtered, m2m_record_filtered = filter_fields(
                TABLE, record, table_fields, rename_fields=rename_fields
            )
            record_obj = finalize_table_data(TABLE, table_fields, record_obj, record_filtered, m2m_record_filtered, **kwargs)
    return record_obj


# check_if_exists: used for checking if a listing exists in db.
def check_if_exists(listing, fetch_and_update_every_single_record):
    obj = get_object_or_None(Property.objects, ddf_id=listing.get("ID", ""))

    if obj is None:
        return False, False, None

    last_updated = None

    try:
        last_updated = parser.parse(listing["LastUpdated"])
    except ValueError:
        logger.debug(f"Property with and id of {row.pk} wasn't able to get a last updated row")
        last_updated = datetime.datetime(2020,5,1)

    if obj.last_updated == last_updated and fetch_and_update_every_single_record == False:
        return True, None, None

    creation_date = obj.creation_date
    if creation_date == None:
        creation_date = timezone.now()
    return True, obj, creation_date


##Maps all DDF tables that are children of the 'office' table in DDF to the db
def add_office_children(office, office_obj):
    for (item, itemClass, item_db_fields, single_element_dict) in office_children:
        if item in office.keys():
            if (
                isinstance(office[item], dict)
                and single_element_dict in office[item].keys()
            ):
                table = office[item][single_element_dict]
            else:
                table = office[item]
            update_table(table, itemClass, db_fields[item_db_fields], office=office_obj)


def wipe_children_table(property_instance=None):
    """
    Wipes the children table for the property.

    NOTE: Still need to refactor this part But this should be one step forward
          on refactoring. We now currently update the base property
          not, just wipe it and replace it. The old code just pretty much
          deletes the property and cascades every children. Which bugs on
          property favorite and recently viewed.
    """

    if property_instance:

        # TODO: Make most of this update. These right here, adds complexity which adds
        # more time to an already slow fetch.

        if hasattr(property_instance, "Info") and property_instance.Info:
            property_instance.Info.delete()

        if (
            hasattr(property_instance, "alternate_url")
            and property_instance.alternate_url
        ):
            property_instance.alternate_url.delete()

        if hasattr(property_instance, "Building") and property_instance.Building:
            property_instance.Building.delete()

        if hasattr(property_instance, "Address") and property_instance.Address:
            property_instance.Address.delete()

        if hasattr(property_instance, "land") and property_instance.land:
            property_instance.land.delete()

        # Specially these, if we have time we need to check which models
        # has an identifier from crea parser and make those update.

        parking = property_instance.Parking.all()

        if parking:
            parking.delete()

        business = property_instance.business_set.all()

        if business:
            business.delete()

        events = property_instance.events.all()

        if events:
            events.delete()

        rooms = property_instance.Room.all()

        if rooms:
            rooms.delete()

        agents = property_instance.Agent.all()

        if agents:
            agents.delete()

        photos = property_instance.Photos.all()

        if photos:
            photos.delete()

        utility = property_instance.utility.all()

        if utility:
            utility.delete()


##Maps agent details table from the DDF to the db
def add_agents_details(agents, property_obj):
    if not isinstance(agents, list):
        agents = [agents]

    for agent in agents:
        agent_obj = update_table(
            agent,
            AgentDetails,
            db_fields["agent_details_fields"],
            connected_property=property_obj,
        )

        if "Office" in agent.keys():
            office_obj = update_table(
                agent["Office"],
                OfficeDetails,
                db_fields["office_details_fields"],
                agent=agent_obj,
            )

            if office_obj:
                add_office_children(agent["Office"], office_obj)

        for (item, itemClass, item_db_fields, single_element_dict) in agent_children:
            if item in agent.keys():
                if (
                    isinstance(agent[item], dict)
                    and single_element_dict in agent[item].keys()
                ):
                    table = agent[item][single_element_dict]
                else:
                    table = agent[item]
                update_table(
                    table, itemClass, db_fields[item_db_fields], agent=agent_obj
                )


##Maps all DDF tables that are children of the 'building' table in DDF to the db
def add_building_children(building, building_obj, property_obj):

    # add children as per db_mapping
    for (item, itemClass, item_db_fields, single_element_dict) in building_children:
        if item in building.keys():
            if (
                isinstance(building[item], dict)
                and single_element_dict in building[item].keys()
            ):
                table = building[item][single_element_dict]
            else:
                table = building[item]
            update_table(
                table, itemClass, db_fields[item_db_fields], connected_property=property_obj
            )


##Maps all DDF tables that are children of the 'property' table in DDF to the db
def add_property_children(listing, property_obj):
    # property_info is PropertyDetails Fields in DDF
    property_info_obj = update_table(
        listing, PropertyInfo, db_fields["property_info_fields"], connected_property=property_obj
    )
    if "Building" in listing.keys():
        building_obj = update_table(
            listing["Building"],
            Building,
            db_fields["building_fields"],
            connected_property=property_obj,
        )

        if building_obj:
            add_building_children(listing["Building"], building_obj, property_obj)

    if "AgentDetails" in listing.keys():
        add_agents_details(listing["AgentDetails"], property_obj)

    # add children as per db_mapping
    for (item, itemClass, item_db_fields, single_element_dict) in property_children:
        if item in listing.keys():
            # Used to assign Children child as some has that in DDF Definition for Example Rooms,Photos.
            if (
                isinstance(listing[item], dict)
                and single_element_dict in listing[item].keys()
            ):
                table = listing[item][single_element_dict]
                # print (table)
            else:
                # if no extra level is there update direct child
                table = listing[item]
            update_table(
                table, itemClass, db_fields[item_db_fields], connected_property=property_obj
            )


# update_records is the main function to update the DDF data which is structured as dictionary to the db tables.
# It received 'new_listings' as a list of dictionaries and it applied the db updates accordingly.
# This function updates only records and is not responsible on handling photos.
def update_records(listing_disk_cache_manager, fetch_and_update_every_single_record=False):

    new_listings_count = 0
    updated_count = 0
    not_updated_count = 0
    missing_address_count = 0
    geolocation_added_count = 0
    geolocation_request_count = 0
    progress_count = 0

    for key in listing_disk_cache_manager.get_all_disk_saved_keys():
        new_listings = listing_disk_cache_manager.get_disk_row(key)
        for listing in new_listings:
            try:
                listing_exist, listing_instance, creation_date = check_if_exists(
                    listing, fetch_and_update_every_single_record
                )
                # used to keep track of orginal creation date
                if listing_exist:
                    if listing_instance:
                        listing["creation_date"] = creation_date
                        logger.debug(
                            "Listing %s is updated old ts:%s new ts:%s",
                            listing["ID"],
                            creation_date,
                            listing["LastUpdated"],
                        )
                        updated_count += 1
                    else:
                        logger.debug("Listing %s found without updates", listing["ID"])
                        not_updated_count += 1
                        continue
                else:
                    logger.debug("Creating New Listing %s", listing["ID"])
                    listing["creation_date"] = listing["LastUpdated"]
                    new_listings_count += 1

                # listing['Multi']=False
                # add property_fields
                # A workaround on the bug where the property and recently viewed, cascades
                # Still ugly, and we still need to refactor the ddf manager if we have the time

                if not listing_instance:
                    property_obj = update_table(
                        listing, Property, db_fields["property_fields"]
                    )
                else:
                    # If the property object already exists, use that instead of creating a new one
                    record_filtered, m2m_record_filtered = filter_fields(
                        Property, listing, db_fields["property_fields"], rename_fields_dict
                    )
                    if record_filtered:
                        error_message = ""
                        try:
                            property_obj = listing_instance
                            property_obj.listing_id = record_filtered.get(
                                "listing_id", ""
                            )
                            property_obj.ddf_id = record_filtered.get("ddf_id", "")
                            property_obj.last_updated = record_filtered.get(
                                "last_updated", None
                            )
                            property_obj.creation_date = record_filtered.get(
                                "creation_date", None
                            )
                            # Bring back to life the properties that was updated that is still here
                            property_obj.is_active = True
                            property_obj.save()
                            wipe_children_table(property_obj)
                        except Exception as e:
                            error_message = e

                        if error_message:
                            logger.error(f"Code Error: {error_message}")

                if property_obj:
                    # add the rest of the records
                    add_property_children(listing, property_obj)

                    logger.info(f"Property with a ddf id {property_obj.ddf_id} is queued for insertion")
                    progress_count += 1
                    logger.info(f"{progress_count} number of property queued for insertion")
                    if "Address" in listing.keys():
                        added_geolocation, request_made = add_geolocation(property_obj)

                        if added_geolocation:
                            geolocation_added_count += 1

                        if request_made:
                            geolocation_request_count += 1

                    else:
                        missing_address_count += 1
                else:
                    logger.error(
                        "Couldn't create Property object for Listing: %s", listing
                    )
            except Exception as e:
                logger.info(e)
                logger.info("Error in updating record for listing: %s", listing["ID"])
                continue

    logger.info("New Listings       : %s", new_listings_count)
    logger.info("Updated Listings   : %s", updated_count)
    logger.info("No Change Listings : %s", not_updated_count)
    logger.info("No Address Listings: %s", missing_address_count)
    logger.info(f"Added geolocation count: {geolocation_added_count}")
    logger.info(f"Geolocation request count: {geolocation_request_count}")

    # Wipe everything, we don't need it anymore
    listing_disk_cache_manager.wipe()

    return True

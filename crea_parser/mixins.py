
import xmltodict

from ddf_manager.settings import CREA_LOGIN_URL, CREA_USERNAME, CREA_PASSWORD
from ddf_manager.rets_lib.session import Session
from ddf_manager.ddf_logger import logger

from core.shortcuts import get_object_or_None, convert_to_snakecase


class CreaModelBaseMetaDataManager(object):
    """
    Base manager for the core models for metadata models
    """

    lookup_name = ""
    resource = ""

    keys = ["LongValue", "Value", "MetadataEntryID", "ShortValue"]

    @classmethod
    def _get_metadata_general_name(cls):
        return f"'{cls.resource}:{cls.lookup_name}'"

    @classmethod
    def _fetch_metadata(cls):
        """
        converts the metadata
        """

        if cls.lookup_name == "" or cls.resource == "":
            logger.error(f"Empty lookupname or resource is detected, raising an error")
            raise AssertionError(
                f"Function fetch metadata expects defined lookupname and resource"
            )

        # TODO: Maybe integrate this with the ddf_client?
        rets_session = Session(CREA_LOGIN_URL, CREA_USERNAME, CREA_PASSWORD)
        login_passed = rets_session.login()
        if login_passed:
            logger.debug("Sending a request...")
            response = rets_session.get_response_lookup_values(cls.resource, cls.lookup_name)
            logger.debug(f"Got back a response of {response}!")
            rets_session.logout()
            return cls._metadata_to_dict(response)
        else:
            logger.error(f"Unable to login on the lookup {cls._get_metadata_general_name()}")
            return []

    @classmethod
    def _metadata_to_dict(cls, response):
        # parse metadata into a dictionary, (homeswipr natural fields)

        # Parse data
        dict_xml = xmltodict.parse(response.text)

        raw_lookup = []

        try:
            raw_lookup = dict_xml.get('RETS').get('METADATA').get('METADATA-LOOKUP_TYPE').get('LookupType')
        except Exception as e:
            logger.error(f"Something went wrong with parsing on the lookup {cls._get_metadata_general_name()}")
            logger.error(f"The error status {e}")
            logger.error(f"raw lookup data {dict_xml}")

        logger.debug(f"Got a raw look up of {raw_lookup}!")

        final_list = []

        for item in raw_lookup:
            final_list.append(dict(item))
        return final_list

    @classmethod
    def _get_keys_length(cls):
        return len(cls.keys)

    @classmethod
    def _map_fields(cls, data):
        params = {}
        for key in cls.keys:
            # NOTE: MetaEntryID should never ever be empty, so this is fine
            params[convert_to_snakecase(key)] = data.get(key, "")

        return params

    @classmethod
    def fetch_and_update_metadata(cls):
        """
        Process metadata to insert it into our database
        """

        logger.info(f"Starting fetch and update metadata resource {cls._get_metadata_general_name()} located on the class {cls.__name__}")

        # Something is concenring about the request
        completed_without_a_hitch = True

        # Base only intercepts 4 fields, long value, value, metadata_entry_id, and short value
        number_of_expected_mapped_fields = cls._get_keys_length()

        data = cls._fetch_metadata()

        if not data:
            completed_without_a_hitch = False

        for item in data:
            logger.debug(f"Found item: {item}")
            exists = get_object_or_None(cls.active_objects, metadata_entry_id=item.get('MetadataEntryID', ""))
            metadata_entry_id = item.get("MetadataEntryID", "")
            short_val = item.get("ShortValue", "")

            # Call out any mismatch keys
            if len(item.keys()) != number_of_expected_mapped_fields:
                logger.warning(
                    f"Number of expected keys mismatch on resource '{cls._get_metadata_general_name()}'' with MetadataEntryId of '{metadata_entry_id}' and value of {short_val}"
                )
                logger.warning(
                    f"Expected {number_of_expected_mapped_fields} keys, recieved {len(item.keys())}"
                )
                completed_without_a_hitch = False

            if not exists and metadata_entry_id != -1:
                try:
                    params = cls._map_fields(item)
                    instance = cls(**params)
                    instance.save()
                    logger.info(
                        f"Inserted a metadata from resource {cls._get_metadata_general_name()} with a MetadataEntryId of {metadata_entry_id} and value of {short_val}"
                    )
                except Exception as e:
                    logger.error(
                        f"Something went wrong on trying to insert on {cls._get_metadata_general_name()} with an error of {e}"
                    )
                    logger.error(
                        f"Item value contains: {item}"
                    )
                    completed_without_a_hitch = False
            else:
                logger.info(
                    f"Skipping a metadata from resource {cls._get_metadata_general_name()} with a MetadataEntryId of {metadata_entry_id} and value of {short_val} due to it already existing"
                )

        if completed_without_a_hitch == False:
            # Logs as critical if the metadata is not inserted properly,
            # we rely on the metadata for a lot of fields!
            logger.critical(
                f"Something is wrong with inserting the {cls._get_metadata_general_name()} metadata! please check the logs for more information"
            )

        return completed_without_a_hitch

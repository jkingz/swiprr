import requests
from core.settings.base import GEOCODE_API_KEY, GEOCODE_URL
from core.shortcuts import get_object_or_None
from crea_parser.models import Geolocation, Property
from django.contrib.gis.geos import Point

from .ddf_logger import logger


###This file is used to add additional information that doesn't exist in the MLS data. Here geolocation is added using a geocoder.
def add_geolocation(listing, override=False):
    made_the_request = False
    json_response = None
    try:
        full_address = f"{listing.Address.street_address} {listing.Address.city} {listing.Address.province} {listing.Address.postal_code}"

        params = {"q": full_address, "apiKey": GEOCODE_API_KEY}

        past_geolocation = get_object_or_None(Geolocation, connected_property=listing)

        if not (past_geolocation and past_geolocation.coordinates) or override:

            # Add a counter to check if request was run
            made_the_request = True

            response = requests.get(GEOCODE_URL, params=params)
            json_response = response.json()

            if response.status_code == 200:
                location = response.json()["items"][0]["position"]
                geolocation, created = Geolocation.objects.get_or_create(
                    connected_property=listing
                )
                geolocation.coordinates = Point(
                    float(location["lng"]), float(location["lat"])
                )
                geolocation.save()
                logger.info(
                    f"Saved a new geolocation for property with a DDF ID of {listing.ddf_id}"
                )
                return True, made_the_request

            logger.error(f"{response.json()}")
            return False, made_the_request
        else:
            logger.info(
                f"listing ID with {listing.ddf_id} already have a coordinates. Skipping listing."
            )
            logger.error(f"The json response of the request: {json_response}")
            return False, made_the_request
    except Exception as e:
        print(e)
        logger.error(e)
        logger.error(f"The json response of the request: {json_response}")
        logger.error("Error in adding Geolocations for listing: %s", listing.ddf_id)
        return False, made_the_request


def add_geolocation_all(override=True):

    geolocation_added_count = 0
    made_the_request_count = 0

    try:
        listings = Property.active_objects.all()
        for listing in listings:
            added_geolocation, made_the_request = add_geolocation(listing, override)

            if added_geolocation:
                geolocation_added_count += 1
                print(
                    f"Saved a new geolocation for property with a DDF ID of {listing.ddf_id}"
                )
                logger.info(
                    f"Saved a new geolocation for property with a DDF ID of {listing.ddf_id}"
                )
                print(
                    f"Added a geolocation, total number of geolocation added {geolocation_added_count}"
                )
                logger.info(
                    f"Added a geolocation, total number of geolocation added {geolocation_added_count}"
                )

            if made_the_request:
                made_the_request_count += 1
                print(
                    f"Added a request, total number of request {made_the_request_count}"
                )
                logger.info(
                    f"Added a request, total number of request {made_the_request_count}"
                )

        logger.info(f"Total geolocations added total: {geolocation_added_count}")
        print(f"Total geolocations added total: {geolocation_added_count}")
        logger.info(f"Total geolocation requests total: {made_the_request_count}")
        print(f"Total geolocation requests total: {made_the_request_count}")

    except Exception as e:
        logger.error(e)
        logger.error("Error in adding Geolocations for all listings")


from ddf_manager.ddf_logger import logger
from django.core.management.base import BaseCommand

from crea_parser.tasks import fetch_ddf_listings

class Command(BaseCommand):
    # The object that collects all commands for ddf
    help = "Refetches properties from the very start (without the timestamp)"


    def handle(self, *args, **options):
        
        logger.warning(
            f"Initialized refetching properties without reading the timestamp..."
        )

        print("Initialized refetching properties without reading the timestamp...")


        logger.warning(
            f"I sure hope you know what you're doing..."
        )

        print("I sure hope you know what you are doing...")

        hour_lock_timeout = 48
        fetch_and_update_every_single_record = True

        fetch_ddf_listings.delay(hour_lock_timeout, fetch_and_update_every_single_record)

        logger.info("Task is sucessfully queued")
        print("Task is sucessfully queued")

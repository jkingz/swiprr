from ddf_manager.db_summary import add_geolocation_all
from django.core.management.base import BaseCommand

from crea_parser.tasks import fetch_ddf_listings

class Command(BaseCommand):
    help = "Reinitializes the geo location process"

    def handle(self, *args, **kwargs):
        override = False
        add_geolocation_all(override)

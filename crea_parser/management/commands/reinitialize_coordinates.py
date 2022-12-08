from ddf_manager.db_summary import add_geolocation_all
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reinitializes the geo location process"

    def handle(self, *args, **kwargs):
        add_geolocation_all()

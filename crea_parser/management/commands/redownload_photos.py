# Commands that is solely used for shell commands
from crea_parser.models import Property
from ddf_manager import settings as ddf_settings
from ddf_manager.ddf_client.ddf_client import DDFClient
from ddf_manager.ddf_logger import logger
from django.core.management.base import BaseCommand
from django.db.models import F


class Command(BaseCommand):
    # The object that collects all commands for ddf
    help = "Redownload photos on the aws or local server"
    ddf_client = None

    def handle(self, *args, **options):

        self.ddf_client = DDFClient(
            ddf_settings.MEDIA_DIR,
            format_type="STANDARD-XML-Encoded",
            s3_reader=ddf_settings.s3_reader,
        )

        self.ddf_client.login()

        records = (
            Property.active_objects.annotate(ID=F("ddf_id"))
            .values("ID")
            .iterator(chunk_size=2000)
        )

        progress = 1
        maximum_count = (
            Property.active_objects.annotate(ID=F("ddf_id")).values("ID").count()
        )

        batch = []

        for record in records:
            batch.append(record.get("ID"))

            logger.info(
                (
                    f"Collecting for batch request on redownload photos: {progress}/{maximum_count}"
                )
            )

            if len(batch) == maximum_count:
                self._download_photos_by_batch(batch)

            if len(batch) == 100:
                self._download_photos_by_batch(batch)

            progress += 1

        self.ddf_client.logout()

    def _download_photos_by_batch(self, batch):
        new_listings, count = self.ddf_client.streamer.retrieve_by_id(batch)
        logger.info("Batch reached, downloading photos")
        self.ddf_client.media_handler.download_photos(new_listings, {})

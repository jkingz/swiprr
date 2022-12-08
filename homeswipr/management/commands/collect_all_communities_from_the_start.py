
# from ddf_manager.ddf_logger import logger
# from django.core.management.base import BaseCommand

# from homeswipr.tasks import collect_all_communities

# class Command(BaseCommand):
#     # The object that collects all commands for ddf
#     help = "Collecting all communites from the start"


#     def handle(self, *args, **options):
        
#         logger.info(
#             f"Initialized collect all communities without reading the timestamp..."
#         )

#         print("Initialized collect all communities without reading the timestamp...")

#         collect_all_communities.delay(True)

#         logger.info("Task collect all communities is sucessfully queued")
#         print("Task collect all communities is sucessfully queued")

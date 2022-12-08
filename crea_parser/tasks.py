from core.celery import app
from core.settings.base import FETCH_CREA_SAMPLE
from ddf_manager import manager as ddf_manager

from core.utils import TaskLock

from ddf_manager.ddf_logger import logger


from crea_parser.submodels.metadata import metadata_models
from homeswipr.tasks import pre_warm_endpoints, email_user_from_saved_search

def fetch_all_metadata():
    # Fetches all available metadata in crea
    # TODO: I think we need to track the last time
    # we fetched metadata, that way we can skip if it's already on our
    # database

    # Something went wrong, or something is concerning about the fetch that we made
    general_error = False

    for model in metadata_models:
        without_a_hitch = model.fetch_and_update_metadata()
        if not without_a_hitch:
            general_error = True
    
    return general_error

@app.task
def fetch_ddf_listings(hour_timeout=2, fetch_and_update_every_single_record=False):

    # Initialize and try to acquire the lock with a 2 hour timeout
    # the timeout is there to release the lock if something went wrong with the server

    fetch_ddf_listings_lock = TaskLock(key="fetch_ddf_listings", timeout=60*60*hour_timeout)

    logger.warning(f"Locking task for {hour_timeout} hour/hours to avoid conflicts...")
    fetch_ddf_listings_lock.check_and_acquire_lock()

    if not fetch_ddf_listings_lock.lock_acquired:
        logger.error(f"Lock wasn't acquired, ignored task to prevent running unique task!")
        return

    logger.warning(f"Lock acquired, proceeding to task executon...")

    something_went_wrong = False

    # TODO: Find a way to make the metadata fetch avoid redudant request
    something_went_wrong = fetch_all_metadata()
    
    if not something_went_wrong:
        ddf_manager.update_server(
            sample=FETCH_CREA_SAMPLE, task_id=fetch_ddf_listings.request.id, 
            fetch_and_update_every_single_record=fetch_and_update_every_single_record
        )
        pre_warm_endpoints.delay()
        email_user_from_saved_search.delay('immediately')

    fetch_ddf_listings_lock.release_lock()

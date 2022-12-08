# Don't delete, this lets the ddf manager know which username and password they should use
from core.settings.base import CREA_LOGIN_URL, CREA_PASSWORD, CREA_USERNAME
from decouple import config

s3_reader = config(
    "SAVE_TO_AWS", default=False, cast=bool
)  # Enable S3, if Disabled Local file System will be used.

SESSION_LISTINGS_COUNT = 100

SECONDS_IN_DAY = 86400

MAX_UPDATE_TIME = 10 * SECONDS_IN_DAY  # 10 Days maximum limit for update time.

PHOTOS_DOWNLOAD_RETRIES = 3

MEDIA_DIR = "media"
LISTING_DIR = MEDIA_DIR + "/" + "listings"
AGENTS_DIR = MEDIA_DIR + "/" + "agents"

LOG_FILENAME = "ddf_task.log"

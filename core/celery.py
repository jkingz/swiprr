from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

from core.settings.base import TIME_ZONE

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.conf.timezone = TIME_ZONE
app.conf.enable_utc = True

app.conf.beat_schedule = {
    "fetch-listings": {
        "task": "crea_parser.tasks.fetch_ddf_listings",
        "schedule": crontab(minute=0, hour='*/3'),
        "args": (),
    },
    # "collect-all-communities": {
    #     "task": "homeswipr.tasks.collect_all_communities",
    #     "schedule": crontab(minute=0, hour='*/6'),
    #     "args": (),
    # },
    "saved-search-mail": {
        "task": "homeswipr.tasks.email_user_from_saved_search",
        # Should fire every 12 noon on MDT
        # as for why it's on 6:00AM, our timezone was changed from
        # mountain daylight time to UTC, I think the change was due
        # to the bookings part, we might want to check how the bookings
        # is implemented before going back to change our timezone
        "schedule": crontab(minute=00, hour=23),
        "args": (),
    },
    "pre-warm-endpoints": {
        "task": "homeswipr.tasks.pre_warm_endpoints",
        "schedule": crontab(minute=00, hour=1),
        "args": (),
    },
}

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

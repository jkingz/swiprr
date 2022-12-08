import math, requests

from core.celery import app
from core.utils import TaskLock
from datetime import datetime
from crea_parser.models import Property, Address
from core.mixins import FrontendUrlConstructionMixin
from core.shortcuts import get_object_or_None
from ddf_manager.ddf_logger import logger
from django.db.models import Count
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.utils.formats import number_format
from django.core.cache import cache
from django.template.loader import get_template
from django.utils import timezone
from django.contrib.sites.models import Site
from homeswipr.models import UserSavedSearch

from .mixins import PropertyHelperMixin


class EmailUserSavedSearchTask(PropertyHelperMixin, FrontendUrlConstructionMixin):
    """
    A class to implement mixin properly.

    NOTE: Celery 4 now adivises against inheriting from
    Task unless you are extending common functionality.
    """

    def run(self, frequency):
        saved_searches = UserSavedSearch.active_objects.filter(frequency=frequency)

        for saved_search in saved_searches:
            final_params = self.construct_advance_search_parameters(saved_search.pk)
            base_property_queryset = self.filter_valid_property(
                self.get_base_property()
            )

            queryset = self.advance_search(base_property_queryset, final_params)

            to_email_properties = queryset.filter(
                creation_date__gt=saved_search.last_checked_date
            ).order_by("-pk").distinct()

            if to_email_properties.count() >= 10:
                to_email_properties = to_email_properties[:10]
            else:
                to_email_properties = to_email_properties[: to_email_properties.count()]

            if to_email_properties:
                if saved_search.user.email:
                    plain_text = get_template("homeswipr/email/email_new_property.txt")
                    raw_html = get_template("homeswipr/email/email_new_property.html")

                    context = {
                        "saved_search": saved_search,
                        "to_email_properties": to_email_properties,
                        # "root_url": Site.objects.get_current().domain,
                        "frontend_url": self.frontend_base_url,
                    }

                    text_content = plain_text.render(context)
                    html_content = raw_html.render(context)

                    subject = f"A new property is found with your saved search titled {saved_search.title}"

                    # Maybe distribute this to another worker?
                    # I think that should make this faster
                    msg = EmailMultiAlternatives(
                        subject, text_content, settings.EMAIL, [saved_search.user.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    number_of_sent = msg.send()

                    if(number_of_sent == 1):
                        logger.info(f"Sent new properties to '{saved_search.user.email}' based on the saved search titled '{saved_search.title} ({saved_search.pk})'")
                    else:
                        logger.error(f"Something went wrong on sending new properties to '{saved_search.user.email} based on the saved search titled '{saved_search.title} ({saved_search.pk})'")
                        logger.error(number_of_sent)

                    # Update date to the most recent one
                    saved_search.last_checked_date = to_email_properties[0].creation_date

                    saved_search.save()

                else:
                    logger.error(
                        f"The user with a pk {saved_search.user.pk} has no email. Did not send email."
                    )


@app.task
def email_user_from_saved_search(frequency='daily'):
    # Emails new property of a saved search to the user
    EmailUserSavedSearchTask().run(frequency)


@app.task
def cache_listing_counts(cache_key):

    # Initialize and try to acquire the lock with a 2 minute timeout
    # the timeout is there to release the lock if something went wrong with the server

    timeout_seconds = 120

    cache_listings_count = TaskLock(key=cache_key, timeout=timeout_seconds)

    logger.warning(f"Locking task for {timeout_seconds} seconds to avoid conflicts...")
    cache_listings_count.check_and_acquire_lock()

    if not cache_listings_count.lock_acquired:
        logger.error(f"Lock wasn't acquired, ignored task to prevent running duplicate of cache listing count task...")
        return

    data = number_format(math.trunc(Property.active_objects.count()))

    cache.set(cache_key, data, 24 * 60 * 60)

    cache_listings_count.release_lock()


@app.task
def pre_warm_endpoints():
    """
        Pre-warms the queries that we used on the property api
        this is especially important on queries that use subqueries,
        this allows postgres to keep the subquery results and avoids re-execution
        of subquery multiple times
    """
    collection_of_urls = [
        reverse('homeswiper:property-recently-added'),
        reverse('homeswiper:property-luxurious-houses'),
    ]

    logger.info("Pre-warming endpoints...")

    # for url in collection_of_urls:
    #     requests.get(f"{Site.objects.get_current()}{url}")

    logger.info("Endpoint pre-warming done")

import os
import shelve
import redis
import requests

import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from pytz import timezone

from core.settings.base import GEOCODE_API_KEY, GEOCODE_URL
from core.shortcuts import get_object_or_None
from crea_parser.models import Geolocation, Property
from django.contrib.gis.geos import Point

from ddf_manager.ddf_logger import logger
from ddf_manager.aws_settings import *
from ddf_manager.settings import *
from ddf_manager.ddf_logger import *

from rest_framework.filters import OrderingFilter

REDIS_CLIENT = redis.Redis()


class TaskLock(object):
    """
    A task lock implemented with redis.
    Mostly used to run task uniquely and prevent duplicate task running.
    """

    key = ""
    timeout = None
    lock = None

    lock_acquired = False

    def __init__(self, key, timeout):
        self.key = key
        self.timeout = timeout

    def check_and_acquire_lock(self):
        """Checks and acquires lock for later use."""

        self.lock = REDIS_CLIENT.lock(self.key, timeout=self.timeout)
        try:
            self.lock_acquired = self.lock.acquire(blocking=False)
            if self.lock_acquired:
                logger.info(f'A lock with a key of {self.key} is acquired.')
            else:
                logger.info(f"Wasn't able to get the lock with a key of {self.key}.")
        except Exception as e:
            logger.error(f"Something went wrong with acquiring the lock with key of {self.key}.")
            logger.error(e)

    def release_lock(self):
        if self.lock:
            self.lock.release()
            logger.info(f"Released a lock with a key of {self.key}.")
        else:
            logger.error(f"Tried to release an undefined lock with a key of {self.key}!")


class HomeswiprMailer(object):
    def __init__(
        self,
        subject,
        recipient,
        html_template,
        text_template,
        attachment=None,
        context=None,
    ):
        assert isinstance(subject, str), "Invalid subject"
        assert isinstance(recipient, str), "Invalid recipient"
        assert isinstance(html_template, str), "Invalid html template path"
        assert isinstance(text_template, str), "Invalid text template path"
        assert context is None or isinstance(
            context, dict
        ), "Invalid content type on context"

        self.context = context
        self.subject = subject
        self.recipient = recipient
        self.sender = settings.EMAIL
        self.html_template = html_template
        self.text_template = text_template
        self.attachment = attachment

    def send_mail(self):
        is_valid = self.validate_email()
        html_template, text_template = self._get_mail_template()
        subject = self._get_mail_subject()
        mail = EmailMultiAlternatives(
            subject, text_template, self.sender, [self.recipient]
        )
        mail.attach_alternative(html_template, "text/html")

        if not is_valid:
            raise ValidationError(_("Invalid email format!"))

        if self.attachment:
            try:
                if self.attachment.name.split(".")[1] == "pdf":
                    mail.attach(
                        "Estimates", self.attachment.read(), "application/pdf"
                    )
                else:
                    mail.attach(
                        "Estimates", self.attachment.read(), "text/plain"
                    )

            except Exception as e:
                raise ValidationError(_(str(e)))

        response = mail.send()
        print(response)

    def _get_mail_subject(self):
        try:
            return get_template(self.subject)
        except TemplateDoesNotExist:
            return self.subject

    def _get_mail_template(self):
        """
        Return a tuple(in order: html_template, text_template) of email template instances if text_template
        and htmml_template are provided and exist else return a single template instance being provided.
        """
        try:
            if self.html_template and self.text_template:
                return (
                    get_template(self.html_template).render(self.context),
                    get_template(self.text_template).render(self.context),
                )

        except TemplateDoesNotExist:
            raise ValidationError(_("Email template Does not exist"))

    def validate_email(self):
        """
        Return either True/False after email is being validated
        """
        try:
            validate_email(self.recipient)
            validate_email(self.sender)
            return True
        except ValidationError:
            return False


class DiskCacheManager(object):
    """
    A dedicated class for disk cache, this should
    make things easier to refactor in the future if
    we want to implement a different implementation.

    Currently using the python native shelfing which
    should create a database file based on a dictinoary

    NOTE: Please make sure to close and ignore the file
    """

    disk_cache = None
    shelf_index = 0
    # Keep count here to lessen things that we count
    disk_cache_count = 0

    # Default name for disk_cache
    # As much as possible, use a specifric name to avoid
    # corruption of a cache
    disk_cache_name = "disk_cache"

    def __init__(self, disk_cache_name=None):
        if disk_cache_name:
            self.disk_cache_name = disk_cache_name

    def initialize_disk_cache(self):
        """
        Initializes disk cache base on a name
        or a default name
        """

        # Enssures that we get a fresh one everytime
        self._remove_old_db()

        self.disk_cache = shelve.open(f"{self.disk_cache_name}")

        # More safety precaution
        self.disk_cache.clear()

    def insert_row_on_disk(self, value):
        """
        Insert a row on disk
        """
        if type(value) != list:
            value = [value]

        self.disk_cache_count += len(value)

        self.disk_cache[f"data-{self.shelf_index}"] = value
        self.shelf_index += 1
        self.disk_cache.sync()

    def get_all_disk_saved_keys(self):
        """
        Get all disk saved keys
        """
        # This might be specific to shelf implementation
        # If we want to have a sql lite implementaion.
        # Just return the keys of the row
        return list(self.disk_cache.keys())

    def get_disk_row(self, key):
        """
        Get row based on a key passed
        """
        return self.disk_cache[key]

    def wipe(self):
        """
        Closes and wipes everything on the memory
        for better storage management
        """
        self.disk_cache.close()
        self._remove_old_db()

    def _remove_old_db(self):

        file_path = os.path.join(settings.PROJECT_PATH, f"{self.disk_cache_name}")
        if os.path.exists(file_path):
            os.remove(file_path)

        with_extension_path = os.path.join(settings.PROJECT_PATH, f"{self.disk_cache_name}.db")
        if os.path.exists(with_extension_path):
            os.remove(with_extension_path)


class FileAttachmentUploadManager(object):

    def __init__(self, listings_path):
        try:
            self.media_dir = MEDIA_DIR
            self.listings_path = listings_path
            self.s3 = boto3.resource(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )
        except Exception as e:
            logger.error(e)

    def upload(self, *args, **kwargs):
        file_instance = kwargs.get('file')
        _dir = f"{self.media_dir}/{self.listings_path}/{file_instance.name}"
        try:
            file_attachment = self.s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
                Key=_dir, Body=file_instance
            )
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )
            meta_data = s3_client.head_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_attachment.key)
            if meta_data["ResponseMetadata"]["HTTPStatusCode"] == 200:
                url = f'{AWS_ROOT_URL}{file_attachment.key}'
                return file_attachment.key
        except Exception as e:
            logger.error(e)
            logger.error("Failed to save photo: %s", _dir)


class PropertyUploadManager(object):

    def __init__(self, images):
        try:
            self.media_dir = MEDIA_DIR
            self.listings_path = "tasks"
            self.images = images
            self.s3 = boto3.resource(
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )

        except Exception as e:
            logger.error(e)

    def upload_image(self, file, order, property_instance_id):
        photo_dir = f"{self.media_dir}/{self.listings_path}/{property_instance_id}"
        photo_path = (
            f"{photo_dir}/{order}.jpg"
        )
        try:
            photo = self.s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
                Key=photo_path, Body=file
            )
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            )
            meta_data = s3_client.head_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=photo.key)
            if meta_data["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return True, photo.key
            ## status code is not 200
            return False, None
        except Exception as e:
            logger.error(e)
            logger.error("Failed to save photo: %s", photo_path)
            return False, None


class PropertyGeolocationManager(object):

    def add_geolocation(property, address, override=True):
        made_the_request = False
        json_response = None
        try:
            full_address = f"{address.street_address} {address.city} {address.province} {address.postal_code}"

            params = {"q": full_address, "apiKey": GEOCODE_API_KEY}

            past_geolocation = get_object_or_None(Geolocation, connected_property=property)

            if not (past_geolocation and past_geolocation.coordinates) or override:

                # Add a counter to check if request was run
                made_the_request = True

                response = requests.get(GEOCODE_URL, params=params)
                json_response = response.json()

                if response.status_code == 200:
                    location = response.json()["items"][0]["position"]
                    geolocation, created = Geolocation.objects.get_or_create(
                        connected_property=property
                    )
                    geolocation.coordinates = Point(
                        float(location["lng"]), float(location["lat"])
                    )
                    geolocation.save()
                    logger.info(
                        f"Saved a new geolocation for property with the ID of {property.pk}"
                    )
                    return True, made_the_request

                logger.error(f"{response.json()}")
                return False, made_the_request
            else:
                logger.info(
                    f"Property with ID {property.pk} already have a coordinates. Skipping listing."
                )
                logger.error(f"The json response of the request: {json_response}")
                return False, made_the_request
        except Exception as e:
            print(e)
            logger.error(e)
            logger.error(f"The json response of the request: {json_response}")
            logger.error("Error in adding Geolocations for listing: %s", property.pk)
            return False, made_the_request


class TimezoneManager(object):
    """
    Custom class to localize timezone.
    """
    def localize_to_canadian_timezone(date):
        canadian_timezone = timezone('Canada/Eastern')
        aware = date.astimezone(canadian_timezone)
        return aware.strftime("%Y-%m-%d, %I:%M %p")


class CaseInsensitiveOrderingFilter(OrderingFilter):

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            return queryset.order_by(*ordering)

        return queryset

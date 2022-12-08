from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError

from model_utils import FieldTracker
from simple_history.models import HistoricalRecords
from core.models import CommonInfo
from .constants import OPTIONAL


class Brokerage(CommonInfo):
    """
    Top Entity for Brokerage.
    """

    name = models.CharField(unique=True, max_length=500, **OPTIONAL)
    email = models.EmailField(unique=True, max_length=225, **OPTIONAL)
    phone_number = models.CharField(unique=True, max_length=50, **OPTIONAL)
    fax_number = models.CharField(max_length=50, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Brokerage - {self.name}"


class Agent(CommonInfo):
    """
    Top Entity for Agent.
    """

    user = models.OneToOneField('users.User', on_delete=models.CASCADE, **OPTIONAL)
    brokerage = models.OneToOneField('components.Brokerage', on_delete=models.CASCADE, **OPTIONAL)
    full_name = models.CharField(max_length=500, **OPTIONAL)
    first_name = models.CharField(max_length=300, **OPTIONAL)
    last_name = models.CharField(max_length=300, **OPTIONAL)
    email = models.EmailField(unique=True, max_length=225, **OPTIONAL)
    phone_number = models.CharField(unique=True, max_length=50, **OPTIONAL)
    fax_number = models.CharField(max_length=50, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Realtor - {self.first_name} {self.last_name}"

    def validate_agent(self):
        email = self.email.lower()
        phone_number = self.phone_number
        if email:
            if Agent.objects.filter(email=email).exists():
                if self.tracker.has_changed('email') and self.tracker.previous('email') != self.email:
                    raise ValidationError({"email": "Email already exists"})
        if phone_number:
            if Agent.objects.filter(phone_number=phone_number).exists():
                if self.tracker.has_changed('phone_number') and \
                        self.tracker.previous('phone_number') != self.phone_number:
                    raise ValidationError({"phone_number": "Phone number already exists"})
        if not (email or phone_number):
            raise ValidationError({"agent": "Please provide email or phone number"})

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
            self.validate_agent()
        super(Agent, self).save(*args, **kwargs)


class LawFirm(CommonInfo):
    """
    Top Entity for LawFirm.
    """

    lawyer_name = models.CharField(max_length=500, **OPTIONAL)
    name = models.CharField(max_length=500, **OPTIONAL)
    address = models.TextField(**OPTIONAL)
    email = models.EmailField(unique=True, max_length=225, **OPTIONAL)
    phone_number = models.CharField(unique=True, max_length=50, **OPTIONAL)
    fax_number = models.CharField(max_length=50, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Law Firm - {self.lawyer_name} {self.name}"


class GoodsIncluded(CommonInfo):
    """
    Top Entity for Goods Included.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    def __str__(self):
        return f"Goods Included - [{self.index}] {self.name}"


class Conditions(CommonInfo):
    """
    Top Entity for Conditions.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    class Meta:
        verbose_name_plural = "Conditions"

    def __str__(self):
        return f"Conditions - [{self.index}] {self.name}"


class ConditionStatus(CommonInfo):
    """
    Top Entity for Condition Status.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    class Meta:
        verbose_name_plural = "Condition Status"

    def __str__(self):
        return f"Condition Status - [{self.index}] {self.name}"


class AdditionalTerms(CommonInfo):
    """
    Top Entity for Additional Terms.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    class Meta:
        verbose_name_plural = "Additional Terms"

    def __str__(self):
        return f"Additional Terms - [{self.index}] {self.name}"


class PaymentMethod(CommonInfo):
    """
    Top Entity for Payment Method.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    def __str__(self):
        return f"Payment Method - [{self.index}] {self.name}"


class PropertyType(CommonInfo):
    """
    Top Entity for Property Type.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    def __str__(self):
        return f"Property Type - [{self.index}] {self.name}"


class Attachments(CommonInfo):
    """
    Top Entity for Attachments.
    """

    name = models.CharField(max_length=500, **OPTIONAL)
    index = models.IntegerField()

    class Meta:
        verbose_name_plural = "Attachments"

    def __str__(self):
        return f"Attachments - [{self.index}] {self.name}"


class UnreadNote(CommonInfo):
    """
    Top Entity for Unread Notes.
    """

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)
    last_date_viewed = models.DateTimeField(auto_now=False, auto_now_add=False, **OPTIONAL)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Unread Notes"
        unique_together = ('user', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Unread Note - [{self.user}] {self.content_object} {self.last_date_viewed}"


class Email(CommonInfo):
    """
    Top Entity for Emails.
    """

    email = models.EmailField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Emails"
        unique_together = ('email', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Email - [{self.content_object}] {self.email}"


class PhoneNumber(CommonInfo):
    """
    Top Entity for Emails.
    """

    phone_number = models.CharField(max_length=15)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Phone Numbers"
        unique_together = ('phone_number', 'content_type', 'object_id')
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Phone Number - [{self.content_object}] {self.phone_number}"

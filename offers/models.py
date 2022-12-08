import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils import FieldTracker
from simple_history.models import HistoricalRecords
from core.models import CommonInfo
from .constants import OPTIONAL

from components.models import UnreadNote


class Offer(CommonInfo):
    """
    Offer for a specific property.
    """

    TYPE = (
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
        ('Both', 'Both'),
    )

    connected_property = models.ForeignKey('crea_parser.Property', on_delete=models.SET_NULL,
                                           related_name='offer_property', **OPTIONAL)
    lead = models.ForeignKey('leads.Lead', on_delete=models.SET_NULL, related_name='offer_lead', **OPTIONAL)
    offer_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    address = models.TextField(**OPTIONAL)
    offer_amount = models.DecimalField(max_digits=50, decimal_places=2, **OPTIONAL)
    offer_open_till = models.DateTimeField(**OPTIONAL)
    offer_status = models.ForeignKey('offers.OfferStatus', on_delete=models.SET_NULL, related_name='offer_status', **OPTIONAL)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, **OPTIONAL)
    representing = models.CharField(max_length=225, choices=TYPE, **OPTIONAL)
    closing_date = models.DateField(**OPTIONAL)
    is_conveyancing = models.BooleanField(default=False)
    property_type = models.CharField(max_length=225, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.connected_property} - ({self.offer_amount})"


class OfferNote(CommonInfo):
    """
    """
    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_notes")
    note = models.TextField(**OPTIONAL)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)
    unread_note = GenericRelation(UnreadNote)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Note for: {self.property_offer} created by - {self.created_by}"


class OfferAdditionalDocuments(CommonInfo):
    """
    """
    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_additional_documents")
    name = models.CharField(max_length=225, **OPTIONAL)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Note for: {self.property_offer} created by - {self.created_by}"


class OfferStatus(CommonInfo):
    """
    Status for a specific offer.
    """

    name = models.CharField(max_length=300)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.name}"


class OfferClient(CommonInfo):
    """
    Buyer / Seller for a specific offer.
    """

    TYPE = (
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
        ('Both', 'Both'),
    )

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_client")
    client = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, **OPTIONAL, related_name="offer_client")
    type = models.CharField(max_length=100, choices=TYPE, **OPTIONAL)

    # This fields are optional, this is only used when we don't have the contact information of the clients.
    first_name = models.CharField(max_length=300, **OPTIONAL)
    last_name = models.CharField(max_length=300, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} by {self.client}"


class OfferAgent(CommonInfo):
    """
    Agent for a specific offer.
    """

    TYPE = (
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
        ('Both', 'Both'),
    )

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_agent")
    agent = models.ForeignKey('components.Agent', on_delete=models.CASCADE, **OPTIONAL, related_name="offer_agent")
    representing = models.CharField(max_length=225, choices=TYPE, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} - {self.agent}"


def offer_requirement_image_path(instance, filename):
    """
    The image file will be uploaded to MEDIA_ROOT/offer_requirements/<offer_uuid>/<filename>
    """

    path = 'offer_requirements/{0}/{1}/{2}'.format(
        instance.property_offer,
        instance.property_offer.offer_uuid,
        filename
    )
    return path


class Requirement(CommonInfo):
    """
    Requirement for a specific offer.
    """

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_requirement")
    image = models.ImageField(upload_to=offer_requirement_image_path)
    note = models.TextField(**OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} - {self.date_created}"


class Condition(CommonInfo):
    """
    Condition for a specific offer.
    """

    STATUS = (
        ('Waiting', 'Waiting'),
        ('Waived', 'Waived'),
        ('Not Waived', 'Not Waived'),
        ('Other', 'Other'),
        ('New', 'New')
    )

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_condition")
    name = models.CharField(max_length=225)
    condition_date = models.DateTimeField(**OPTIONAL)
    status = models.CharField(max_length=225, choices=STATUS, default='New')

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} - {self.name}"


class AdditionalTerm(CommonInfo):
    """
    Additional term for a specific offer.
    """

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_additional_term")
    name = models.CharField(max_length=225)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} - {self.name}"


class Deposit(CommonInfo):
    """
    Deposit for a specific offer.
    """

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_deposit")
    deposit_amount = models.DecimalField(max_digits=50, decimal_places=2)
    deposit_date = models.DateField(**OPTIONAL)
    is_additional = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=225, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} - {self.deposit_amount}"


class GoodsIncluded(CommonInfo):
    """
    Goods included for a specific offer.
    """

    property_offer = models.ForeignKey('offers.Offer', on_delete=models.CASCADE, **OPTIONAL,
                                       related_name="property_offer_goods_included")
    name = models.CharField(max_length=225)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"{self.property_offer} - {self.name}"

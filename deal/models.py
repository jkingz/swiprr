from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils import FieldTracker
from simple_history.models import HistoricalRecords

from core.models import CommonInfo
from deal.constants import OPTIONAL

from components.models import UnreadNote

REPRESENTATION = [
    ('Buy', 'Buy'),
    ('Sell', 'Sell'),
    ('Both', 'Both')
]


class AdditionalTerm(CommonInfo):
    """
    Additional Terms for the Deal.
    """
    name = models.CharField(max_length=250, **OPTIONAL)
    note = models.TextField(**OPTIONAL)
    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        **OPTIONAL,
        related_name="deal_additional_terms",
    )
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.name}"


class Brokerage(CommonInfo):
    """
    Brokerage assigned/representing on the deal.
    """
    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    brokerage = models.ForeignKey(
        "components.Brokerage",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    representing = models.CharField(max_length=25, choices=REPRESENTATION, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.brokerage} representing {self.representing}"


class Commission(CommonInfo):
    """
    Listing/Selling Commission for Deals.
    """
    REPRESENTATION = [
        ('Listing', 'Listing'),
        ('Selling', 'Selling')
    ]

    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    agent = models.ForeignKey(
        "components.Agent",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    percentage = models.DecimalField(max_digits=50, decimal_places=2, **OPTIONAL)
    value_dollars = models.DecimalField(max_digits=50, decimal_places=2, **OPTIONAL)
    GST = models.DecimalField(max_digits=50, decimal_places=2, **OPTIONAL)
    total = models.DecimalField(max_digits=50, decimal_places=2, **OPTIONAL)
    notes = models.TextField(**OPTIONAL)
    type = models.CharField(max_length=25, choices=REPRESENTATION, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.type} {self.deal}"


class Condition(CommonInfo):
    """
    Deal conditions.
    """
    STATUS = [
        ('Waiting', 'Waiting'),
        ('Waived', 'Waived'),
        ('Not Waived', 'Not Waived'),
        ('Other', 'Other'),
        ('New', 'New')
    ]

    deal = models.ForeignKey(
        "deal.Deal",
        related_name="deal_conditions",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    name = models.CharField(max_length=250, **OPTIONAL)
    status = models.CharField(max_length=25, choices=STATUS, default='New')
    date = models.DateTimeField(auto_now=False, auto_now_add=False, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.name} included for {self.deal}"


class Client(CommonInfo):
    """
    Clients connected to the deal.
    """
    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    client = models.ForeignKey(
        "contacts.Contact",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    client_type = models.CharField(max_length=25, choices=REPRESENTATION, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.client} representing {self.client_type}"


class Deal(CommonInfo):
    """
    Deal Transactions.
    """
    connected_property = models.ForeignKey(
        "crea_parser.Property",
        on_delete=models.SET_NULL,
        related_name="connected_deal_property",
        **OPTIONAL
    )
    possession_date = models.DateTimeField(auto_now=False, auto_now_add=False)
    is_conveyancing = models.BooleanField(default=False)
    representing = models.CharField(max_length=25, choices=REPRESENTATION, default='Buy')
    sale_price = models.DecimalField(max_digits=19, decimal_places=2)
    sale_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    address = models.CharField(max_length=1000, **OPTIONAL)
    status = models.ForeignKey("deal.DealStatus", on_delete=models.CASCADE, **OPTIONAL)
    connected_offer = models.ForeignKey(
        "offers.Offer",
        on_delete=models.PROTECT,
        related_name="connected_deal_offer",
        **OPTIONAL
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT
    )
    property_type = models.CharField(max_length=225, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"Deal for {self.address}"


class DealStatus(CommonInfo):
    """
    Available Status for Deals
    """
    name = models.CharField(max_length=250, **OPTIONAL, unique=True)

    def __str__(self):
        return self.name


class Deposit(CommonInfo):
    """
    Initial Deposit and Additional Deposit for a Deal is stored here.
    """
    deal = models.ForeignKey(
        "deal.Deal",
        related_name="deal_deposit",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    date = models.DateTimeField(auto_now=False, auto_now_add=False)
    payment_method = models.CharField(max_length=100, **OPTIONAL)
    is_additional = models.BooleanField(default=False)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.deal} -  {self.amount} "


class GoodsIncluded(CommonInfo):
    """
    Goods Included with the deal.
    """
    name = models.CharField(max_length=250, **OPTIONAL)
    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE
    )
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.name} included for {self.deal}"


class Realtor(CommonInfo):
    """
    Realtor assigned/representing on the deal.
    """
    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    agent = models.ForeignKey(
        "components.Agent",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    representing = models.CharField(max_length=25, choices=REPRESENTATION, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.agent} representing {self.representing}"


class LawFirm(CommonInfo):
    """
    LawFirm assigned/representing on the deal.
    """
    deal = models.ForeignKey(
        "deal.Deal",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    lawfirm = models.ForeignKey(
        "components.LawFirm",
        on_delete=models.CASCADE,
        **OPTIONAL
    )
    representing = models.CharField(max_length=25, choices=REPRESENTATION, **OPTIONAL)
    history = HistoricalRecords()

    tracker = FieldTracker()

    def __str__(self):
        return f"{self.lawfirm} representing {self.representing}"


class DealNote(CommonInfo):
    """
    Notes for deals.
    """
    deal = models.ForeignKey('deal.Deal', on_delete=models.CASCADE, **OPTIONAL, related_name="deal_note")
    note = models.TextField(**OPTIONAL)
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE, **OPTIONAL)
    unread_note = GenericRelation(UnreadNote)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Note for: {self.deal} created by - {self.created_by}"


class DealAdditionalDocument(CommonInfo):
    """
    Additional document for deals.
    """
    deal = models.ForeignKey('deal.Deal', on_delete=models.CASCADE, **OPTIONAL,
                             related_name="deal_additional_document")
    name = models.CharField(max_length=225, **OPTIONAL)

    history = HistoricalRecords()
    tracker = FieldTracker()

    def __str__(self):
        return f"Additional document for: {self.deal} - {self.name}"

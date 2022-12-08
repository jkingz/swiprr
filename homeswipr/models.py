from core.models import CommonInfo
from crea_parser.models import AgentDetails, Parking, Property, PropertyInfo
from crea_parser.submodels.metadata import (
    PropertyOwnershipType, PropertyParkingType, PropertyBuildingType,
    PropertyBasementType
)
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from model_utils import FieldTracker
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from phonenumber_field.modelfields import PhoneNumberField

from core.shortcuts import get_object_or_None
from core.constants import OPTIONAL


class PropertyFavorite(CommonInfo):
    """
    The model that is connected to the parent favorite.
    If we just need the user's property favorites, use this.
    """

    # property is a reserved key word
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="property_favorite"
    )
    favorited_property = models.ForeignKey(Property, on_delete=models.CASCADE)

    def __str__(self, *args, **kwargs):
        return f"{self.user} favorites {self.favorited_property}"


class AgentFavorite(CommonInfo):
    """
    The model that is connected to the parent favorite.
    If we just need the user's agent favorites, use this.
    """

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="agent_favorite"
    )
    favorited_agent = models.ForeignKey(AgentDetails, on_delete=models.CASCADE)

    def __str__(self, *args, **kwargs):
        return f"{self.user} favorites {self.favorited_agent}"


class UserSavedSearch(CommonInfo):
    """
    The model that saves the saved search for the user
    """

    FREQUENCY_CHOICES = [
        ('daily', 'daily'),
        ('immediately', 'immediately')
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    agents = models.ManyToManyField(
        'users.User', blank=True, related_name="saved_search_agents"
    )

    title = models.CharField(max_length=225)

    # NOTE: I think all the fields below could be replaced with json field.
    # I think it would be easier to manipulate if that's the case

    # General text search that hits the a lot of fields
    search_text = models.TextField(default="", null=True, blank=True)
    city_list = ArrayField(
        models.CharField(max_length=225, null=True, blank=True), null=True, blank=True
    )

    # The price boundary for the search
    lower_boundary_price_range = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )
    upper_boundary_price_range = models.DecimalField(
        max_digits=102, decimal_places=2, null=True, blank=True
    )

    least_amount_of_bedroom = models.SmallIntegerField(null=True, blank=True)
    least_amount_of_bathroom = models.SmallIntegerField(null=True, blank=True)

    # Store these into a list field for more convenience
    # These should be fully supported by postgres
    ownership_type_ids = ArrayField(
        models.IntegerField(), null=True, blank=True
    )
    transaction_type_id = models.IntegerField(
        null=True, blank=True
    )
    transaction_type_id_list = ArrayField(
        models.IntegerField(), null=True, blank=True
    )
    parking_type_ids = ArrayField(
        models.IntegerField(), null=True, blank=True
    )

    year_built = models.IntegerField(null=True, blank=True)
    year_built_condition = models.TextField(default="", null=True, blank=True)

    size = models.CharField(max_length=100, null=True, blank=True)

    # Initial implementation didn't get the metadata,
    # we need to change the implementation to intger with the metadata
    building_type_list = ArrayField(
        models.IntegerField(), null=True, blank=True
    )

    community_search_text = models.TextField(default="", blank=True)
    community_list_search_text = ArrayField(
        models.CharField(max_length=225), null=True, blank=True
    )

    # A nullable boolean field, null means. It could be both
    has_video = models.BooleanField(null=True)

    from_creation_date = models.DateTimeField(blank=True, null=True)
    until_creation_date = models.DateTimeField(blank=True, null=True)
    from_listing_contract_date = models.DateTimeField(blank=True, null=True)
    until_listing_contract_date = models.DateTimeField(blank=True, null=True)

    zoning_keyword = models.TextField(default="", blank=True)
    has_garage = models.TextField(default="", blank=True)

    basement_type = models.TextField(default="", blank=True)
    basement_type_list = ArrayField(
        models.IntegerField(), null=True, blank=True
    )

    has_suite = models.TextField(default="", blank=True)
    architectural_style = ArrayField(
        models.IntegerField(), null=True, blank=True
    )

    # Last date the user saved search was checked or the last date of the property
    # that was emailed
    last_checked_date = models.DateTimeField(auto_now_add=True)

    # this field is filled when the saved search is created by an admin/
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="created_by",
    )

    # this field is for the email notification for saved search listings.
    frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES,
        default='daily'
    )

    tracker = FieldTracker()

    class Meta:
        verbose_name_plural = "User saved searches"

    def __str__(self):
        return f'"{self.title}" by {self.user}'

    @property
    def community_list_search_text_display(self):
        if self.community_list_search_text:
            return ", ".join(self.community_list_search_text)
        return ""

    @property
    def building_type_list_display(self):
        final_array = self.array_field_representation(
            PropertyBuildingType, self.building_type_list
        )
        if final_array:
            return final_array
        else:
            ""

    @property
    def basement_type_list_display(self):
        final_array = self.array_field_representation(
            PropertyBasementType, self.basement_type_list
        )
        if final_array:
            return final_array
        else:
            ""

    @property
    def city_list_display(self):
        if self.city_list:
            return ", ".join(self.city_list)
        return ""

    def get_ownership_type_ids_display(self):
        return self.array_field_representation(
            PropertyOwnershipType, self.ownership_type_ids
        )

    def get_parking_type_ids_display(self):
        return self.array_field_representation(
            PropertyParkingType, self.parking_type_ids
        )

    @classmethod
    def pull_choice_field_representation(cls, model, id):
        return get_object_or_None(model.active_objects, metadata_entry_id=id).short_value

    def array_field_representation(self, model, values):
        string_representation_ownership_type = []

        if values is not None and len(values):
            for value in values:
                string_representation_ownership_type.append(
                    self.pull_choice_field_representation(model, value)
                )
            return ", ".join(string_representation_ownership_type)
        return []


class SavedSearchClient(CommonInfo):
    """
        Saved Search client's allowing us to assign multiple clients to a specific saved search.
    """

    saved_search = models.ForeignKey(
        UserSavedSearch, on_delete=models.CASCADE, related_name="saved_search_clients", null=True
    )

    first_name = models.CharField(max_length=225, null=True)
    last_name = models.CharField(max_length=225, null=True)
    email = models.EmailField(max_length=225, null=True)
    phone_number = PhoneNumberField(null=True)

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return f"{self.booking} by {self.user}"


class FrequentlyAskedQuestion(CommonInfo):
    """
    This model is dedicated content for FAQ page.
    """

    question = models.CharField(max_length=100)  # topic
    answer = models.CharField(max_length=5000)  # content

    def __str__(self, *args, **kwargs):
        return f"{self.question}"


class PropertyInquiry(CommonInfo):
    """"""

    OPEN = "OPEN"
    CLOSE = "CLOSE"
    PENDING = "PENDING"

    STATUS = ((OPEN, "Open"), (PENDING, "Pending"), (CLOSE, "Close"))

    first_name = models.CharField(_("first name"), max_length=30, null=True, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, null=True, blank=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    phone_number = models.CharField(
        _("phone number"), max_length=15, blank=True, null=True
    )
    fk_email = models.ForeignKey(
        "users.HomeswiprLead", on_delete=models.CASCADE, **OPTIONAL
    )
    question = models.TextField()
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="property_inquiries",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=10, choices=STATUS, default=OPEN)
    inquired_property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="inquiries"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name_plural = "Property Inquiries"

    def __str__(self, *args, **kwargs):
        return f"{self.first_name} {self.question}"


class Brokerage(CommonInfo):
    """
    Top Entity for Brokerage.
    """
    name = models.CharField(max_length=500)
    email = models.EmailField(max_length=225, **OPTIONAL, unique=True)
    phone_number = models.CharField(max_length=50, **OPTIONAL, unique=True)
    fax_number = models.CharField(max_length=50, **OPTIONAL)

    def __str__(self):
        return f"Brokerage - {self.name}"


class Agent(CommonInfo):
    """
    Top Entity for Agent.
    """
    full_name = models.CharField(max_length=500, **OPTIONAL)
    first_name = models.CharField(max_length=300, **OPTIONAL)
    last_name = models.CharField(max_length=300, **OPTIONAL)
    email = models.EmailField(unique=True, max_length=225, **OPTIONAL)
    phone_number = models.CharField(unique=True, max_length=50, **OPTIONAL)
    fax_number = models.CharField(max_length=50, **OPTIONAL)
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, **OPTIONAL, related_name="realtor_user")
    brokerage = models.OneToOneField('homeswipr.Brokerage', on_delete=models.CASCADE, **OPTIONAL, related_name="realtor_brokerage")

    def __str__(self):
        return f"Realtor - {self.full_name}"


class LawFirm(CommonInfo):
    """
    Top Entity for LawFirm.
    """
    lawyer_name = models.CharField(max_length=500)
    name = models.CharField(max_length=500)
    address = models.TextField()
    email = models.EmailField(max_length=225, **OPTIONAL,  unique=True)
    phone_number = models.CharField(max_length=50, **OPTIONAL, unique=True)
    fax_number = models.CharField(max_length=50,  **OPTIONAL)

    def __str__(self):
        return f"Law Firm - {self.lawyer_name} {self.name}"

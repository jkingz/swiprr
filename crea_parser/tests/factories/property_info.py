from random import randint

import factory
from core.tests.utils import produce_fake_random_words_or_none
from crea_parser.models import PropertyInfo
from crea_parser.submodels.metadata import PropertyBoard, PropertyOwnershipType, PropertyPropertyType, PropertyTransactionType, PropertyAmenityNearby
from django.utils import timezone
from faker import Faker

fake = Faker()


class PropertyInfoFactory(factory.django.DjangoModelFactory):
    """
    PropertyInfo Factory
    """

    class Meta:
        model = PropertyInfo

    # Using bank number. We could change this if we could fake a more suitable fake
    ddf_id = factory.LazyAttribute(lambda o: fake.bban())
    # Need to check other values, currently ddf is the only thing we can see on local
    listing_type = factory.LazyAttribute(lambda o: 1)

    last_updated = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )

    price = factory.LazyAttribute(
        lambda o: fake.pydecimal(right_digits=2, max_value=100000000000)
    )

    lease = factory.LazyAttribute(
        lambda o: fake.pydecimal(right_digits=2, max_value=100000000000)
    )

    board = factory.Iterator(PropertyBoard.active_objects.all())
    additional_information_indicator = factory.LazyAttribute(lambda o: fake.sentence())
    transaction_type = factory.Iterator(PropertyTransactionType.active_objects.all())

    listing_contract_date = factory.LazyAttribute(
        lambda o: fake.past_datetime(tzinfo=timezone.get_current_timezone())
    )

    property_type = factory.Iterator(PropertyPropertyType.active_objects.all())

    public_remarks = factory.LazyAttribute(lambda o: fake.paragraph())

    ownership_type = factory.Iterator(PropertyOwnershipType.active_objects.all())

    connected_property = factory.SubFactory(
        "crea_parser.tests.factories.property.PropertyFactory", property_info=None
    )
